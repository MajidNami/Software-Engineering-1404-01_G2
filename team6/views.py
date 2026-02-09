from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import uuid
from django.contrib import messages
from django.utils.text import slugify
from .models import WikiArticle,WikiTag, WikiCategory, WikiArticleRevision, WikiArticleReports
from deep_translator import GoogleTranslator
import requests
from django.db import IntegrityError
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .services.llm_service import FreeAIService

TEAM_NAME = "team6"

# --- Base views ---
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    articles = WikiArticle.objects.filter(status='published')
    return render(request, "team6/index.html", {"articles": articles})

# لیست مقالات
@method_decorator(never_cache, name='dispatch')#برای اینکه بدون رفرش بازدید اوکی شه
class ArticleListView(ListView):
    model = WikiArticle
    template_name = 'team6/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        queryset = WikiArticle.objects.filter(status='published')
        q = self.request.GET.get('q')
        cat = self.request.GET.get('category')
        search_type = self.request.GET.get('search_type', 'direct')

        if q:  # جستجوی مستقیم یا معنایی
            if search_type == 'semantic':
                queryset = queryset.filter(
                    Q(title_fa__icontains=q) | 
                    Q(body_fa__icontains=q) |
                    Q(summary__icontains=q)
                ).distinct()
            else:  # جستجوی مستقیم
                queryset = queryset.filter(
                    Q(title_fa__icontains=q) | 
                    Q(body_fa__icontains=q)
                )
        
        if cat:  # فیلتر دسته‌بندی
            queryset = queryset.filter(category__slug=cat)
            
        sort_by = self.request.GET.get('sort', 'alphabetical')
        if sort_by == 'views':
            queryset = queryset.order_by('-view_count')
        else:
            queryset = queryset.order_by('title_fa') # سورت الفبایی پیش‌فرض
            
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = WikiCategory.objects.all()
        return context

# ایجاد مقاله
class ArticleCreateView(CreateView):
    model = WikiArticle
    template_name = 'team6/article_form.html'
    
    # لیست فیلدهایی که می‌خواهیم در فرم باشند
    fields = ['title_fa', 'place_name', 'body_fa', 'summary']
    
    # اضافه کردن چک لاگین در dispatch
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "برای ایجاد مقاله باید وارد سیستم شوید.")
            return redirect('/auth/')  # هدایت به صفحه لاگین سرویس مرکزی
        return super().dispatch(request, *args, **kwargs)

    # اضافه کردن چک لاگین در dispatch
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/auth/')  # هدایت به صفحه لاگین سرویس مرکزی
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        article = form.save(commit=False)
        # پر کردن اطلاعات نویسنده و ویرایشگر
        article.author_user_id = self.request.user.id
        article.last_editor_user_id = self.request.user.id
        article.status = 'published'
        
        # دریافت category_id از فرم
        category_id = self.request.POST.get('category')
        if category_id:
            try:
                article.category = WikiCategory.objects.get(id_category=category_id)
            except WikiCategory.DoesNotExist:
                messages.error(self.request, "دسته‌بندی انتخاب شده معتبر نیست.")
                return self.form_invalid(form)
        else:
            messages.error(self.request, "لطفاً یک دسته‌بندی انتخاب کنید.")
            return self.form_invalid(form)
        
        # ساخت slug از عنوان فارسی
        # ابتدا از عنوان فارسی slug می‌سازیم
        title_slug = slugify(article.place_name, allow_unicode=False)
        
        # اگر slug خالی بود یا تکراری بود، از UUID استفاده می‌کنیم
        if not title_slug or WikiArticle.objects.filter(slug=title_slug).exists():
            article.slug = str(uuid.uuid4())[:12]
        else:
            article.slug = title_slug
        
        # ساخت URL مقاله
        article.url = f"/team6/article/{article.slug}/"

        try:
            article.title_en = GoogleTranslator(source='fa', target='en').translate(article.title_fa)
            article.body_en = GoogleTranslator(source='fa', target='en').translate(article.body_fa)
        except Exception as e:
            # اگر ترجمه انجام نشد، پیش‌فرض انگلیسی برابر فارسی باشد
            article.title_en = article.title_fa
            article.body_en = article.body_fa
            
        # خلاصه متن
        # article.summary = summarize_text(article.body_fa)
        # ذخیره مقاله
        
        try:
            llm = FreeAIService()
            ai_summary = llm.generate_summary(article.body_fa)
            ai_tags = llm.extract_tags(article.body_fa, article.title_fa)

            article.summary = ai_summary
            article.save(update_fields=['summary'])

            # حذف تگ‌های قبلی و اضافه کردن تگ‌های AI
            article.tags.clear()
            for tag_name in ai_tags:
                tag, _ = WikiTag.objects.get_or_create(
                    title_fa=tag_name,
                    defaults={'slug': tag_name.replace(' ', '-').replace('‌', '-')[:50],
                            'title_en': tag_name}
                )
                article.tags.add(tag)
        except Exception as e:
            # اگر AI خراب شد، مقاله با خلاصه دستی ذخیره شود
            print("AI summary/tags error:", e)
        
        article.save()
        WikiArticleRevision.objects.create(
            article=article,
            revision_no=1,
            body_fa=article.body_fa,
            body_en=article.body_en,  
            editor_user_id=self.request.user.id,
            change_note="ایجاد اولیه مقاله"
        )
        # اضافه کردن پیام موفقیت
        messages.success(self.request, f"✅ مقاله '{article.title_fa}' با موفقیت ایجاد شد!")
        
        # ریدایرکت به صفحه لیست مقالات
        return redirect('team6:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = WikiCategory.objects.all()
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if 'slug' in form.fields:
            del form.fields['slug']
        return form

# ویرایش مقاله
@login_required
def edit_article(request, slug):
    article = get_object_or_404(WikiArticle, slug=slug)
    if article.author_user_id != request.user.id:
        return render(request, 'team6/not_allowed.html', {
            'message': '✋ فقط نویسنده‌ی مقاله می‌تواند مقاله را ویرایشش کند'
        })
    
    # این متغیر را باید از خود مقاله بگیریم
    current_rev = WikiArticleRevision.objects.filter(article=article).count() + 1

    if request.method == "POST":
        # ذخیره نسخه قبلی در تاریخچه
        WikiArticleRevision.objects.create(
            article=article,
            revision_no=current_rev,
            body_fa=request.POST.get('body_fa', article.body_fa),
            editor_user_id=request.user.id,
            change_note=request.POST.get('change_note', 'ویرایش بدون توضیح')
        )

        # آپدیت مقادیر مقاله
        article.title_fa = request.POST.get('title_fa', article.title_fa)
        article.body_fa = request.POST.get('body_fa', article.body_fa)
        article.summary = request.POST.get('summary', article.summary)
        
        # آپدیت دسته‌بندی اگر تغییر کرده
        category_id = request.POST.get('category')
        if category_id:
            try:
                article.category = WikiCategory.objects.get(id_category=category_id)
            except WikiCategory.DoesNotExist:
                pass
        tags_input = request.POST.get('tags', '')
        article.tags.clear()
        for tag_name in [t.strip() for t in tags_input.split(",") if t.strip()]:
            tag, _ = WikiTag.objects.get_or_create(
                title_fa=tag_name,
                defaults={'slug': tag_name.replace(' ', '-').replace('‌', '-')[:50],
                        'title_en': tag_name}
            )
            article.tags.add(tag)
        
        article.current_revision_no = current_rev + 1
        article.last_editor_user_id = request.user.id
        # article.featured_image_url = request.POST.get('featured_image_url', article.featured_image_url)
        article.save()

        messages.success(request, "✅ مقاله با موفقیت ویرایش شد")
        return redirect('team6:article_detail', slug=article.slug)

    # برای GET، فرم و دسته‌بندی‌ها را به قالب می‌فرستیم
    categories = WikiCategory.objects.all()
    return render(request, 'team6/article_edit.html', {
        'article': article,
        'categories': categories,
    })

# گزارش مقاله 
def article_revision_detail(request, slug, revision_no):
    article = get_object_or_404(WikiArticle, slug=slug)
    revision = get_object_or_404(
        WikiArticleRevision,
        article=article,
        revision_no=revision_no
    )

    return render(request, 'team6/article_revision_detail.html', {
        'article': article,
        'revision': revision,
    })

def report_article(request, slug):
    if not request.user.is_authenticated:
        return redirect('/auth/')
    
    article = get_object_or_404(WikiArticle, slug=slug)
    
    if request.method == "POST":
        reporter_id = request.user.id 
        try:
            WikiArticleReports.objects.create(
                article=article,
                reporter_user_id=reporter_id,
                report_type=request.POST.get('type', 'other'),
                description=request.POST.get('desc', '')
            )
            return render(request, 'team6/report_success.html', {'article': article})
        except IntegrityError:
            # این خطا زمانی رخ می‌دهد که کاربر قبلاً برای این مقاله گزارش ثبت کرده باشد
            messages.warning(request, "شما قبلاً این مقاله را گزارش داده‌اید و گزارش شما در دست بررسی است.")
            return redirect('team6:article_detail', slug=slug)
    return render(request, 'team6/article_report.html', {'article': article})

# نمایش نسخه‌ها
def article_revisions(request, slug):
    article = get_object_or_404(WikiArticle, slug=slug)
    revisions = WikiArticleRevision.objects.filter(
    article=article
        ).exclude(
            revision_no__isnull=True
        ).order_by('-created_at')
    return render(request, 'team6/article_revisions.html', {
        'article': article, 
        'revisions': revisions
    })

# نمایش جزئیات مقاله
def article_detail(request, slug):
    try:
        article = get_object_or_404(WikiArticle, slug=slug)
        
        # گرفتن لیست مقالات دیده شده در این سشن (اگر نبود، لیست خالی)
        viewed_articles = request.session.get('viewed_articles', [])
        
        # افزایش بازدید
        #  چک کردن اینکه آیا این مقاله خاص قبلاً توسط این یوزر دیده شده یا نه
        if slug not in viewed_articles:
            if hasattr(article, 'view_count'):
                article.view_count += 1
                # استفاده از update_fields برای امنیت و سرعت بیشتر دیتابیس
                article.save(update_fields=['view_count'])
        #  اضافه کردن اسلاگ این مقاله به لیست دیده‌شده‌های یوزر
            viewed_articles.append(slug)
            request.session['viewed_articles'] = viewed_articles
            # اطلاع به جنگو که سشن تغییر کرده و باید ذخیره شود
            request.session.modified = True
        return render(request, 'team6/article_detail.html', {'article': article})
    except Exception as e:
        print(f"Error: {e}") 
        return render(request, 'team6/errors/500.html', status=500)

def calculate_article_score(article):
    """
    تابع مستقل برای محاسبه امتیاز مقاله.
    فعلاً فقط بر اساس بازدید، اما قابل گسترش به پارامترهای دیگر.
    """
    views = article.view_count or 0
    #میشه لگاریتمی یا مدل دیگه هم انجام داد
    score = views
    
    # می‌توانی اینجا شرط‌های دیگری هم اضافه کنی
        
    return round(score, 2)

# API برای محتوای ویکی
def get_wiki_content(request):
    place_query = request.GET.get('place', None)
    
    if not place_query:
        return JsonResponse({"error": "پارامتر place الزامی است"}, status=400)
    
    # ۱. پیدا کردن تمام مقالات مرتبط
    articles = WikiArticle.objects.filter(
        Q(place_name__icontains=place_query) | 
        Q(title_fa__icontains=place_query),
        status='published'
    )

    if not articles.exists():
        return JsonResponse({"message": "محتوایی برای این مکان یافت نشد"}, status=404)

    # ما لیست را بر اساس تابع امتیازدهی سورت می‌کنیم
    best_article = max(articles, key=lambda x: calculate_article_score(x))
    # ساخت خروجی
    data = {
        "id": str(best_article.id) if hasattr(best_article, 'id') else str(best_article.slug),
        "title": best_article.title_fa,
        "place_name": best_article.place_name,
        "category": best_article.category.title_fa if best_article.category else "",
        "tags": list(best_article.tags.values_list('title_fa', flat=True)) if hasattr(best_article, 'tags') else [],
        "summary": best_article.summary if hasattr(best_article, 'summary') else "",
        "description": best_article.body_fa,
        "url": f"/team6/best_article/{best_article.slug}/",
        "updated_at": best_article.updated_at.isoformat() if hasattr(best_article, 'updated_at') else ""
    }
    
    # اضافه کردن تصویر اگر وجود دارد
    # if hasattr(article, 'featured_image_url') and article.featured_image_url:
    #     data["images"] = [article.featured_image_url]
    
    return JsonResponse(data)



@login_required
def delete_article(request, slug):
    # پیدا کردن مقاله یا نمایش ۴۰۴
    article = get_object_or_404(WikiArticle, slug=slug)
    
    # کنترل دسترسی: فقط نویسنده اصلی
    # نکته: چون author_user_id در مدل شما UUID است، آن را با آیدی کاربر مقایسه می‌کنیم
    if str(article.author_user_id) != str(request.user.id):
        messages.error(request, "✋ خطای امنیتی: شما نویسنده این مقاله نیستید و اجازه حذف آن را ندارید.")
        return redirect('team6:article_detail', slug=slug)

    if request.method == "POST":
        article.delete()
        messages.success(request, "✅ مقاله با موفقیت حذف شد.")
        return redirect('team6:index')
    
    return render(request, 'team6/article_confirm_delete.html', {'article': article})



def error_404(request, exception):
    return render(request, 'team6/errors/404.html', status=404)

def error_500(request):
    return render(request, 'team6/errors/500.html', status=500)

def error_403(request, exception):
    return render(request, 'team6/errors/403.html', status=403)

def error_400(request, exception):
    return render(request, 'team6/errors/400.html', status=400)

# @csrf_exempt
# def generate_ai_content_api(request, slug):
#     """تولید دستی خلاصه و تگ با AI"""
#     if request.method != 'POST':
#         return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#     article = get_object_or_404(WikiArticle, slug=slug)
    
#     # فقط نویسنده
#     if str(article.author_user_id) != str(request.user.id):
#         return JsonResponse({'error': 'شما مجاز به انجام این عمل نیستید'}, status=403)
    
#     try:
#         llm_service = FreeAIService()
        
#         # تولید خلاصه جدید
#         new_summary = llm_service.generate_summary(article.body_fa)
        
#         # استخراج تگ‌های جدید
#         new_tags = llm_service.extract_tags(article.body_fa, article.title_fa)
        
#         # ذخیره خلاصه
#         article.summary = new_summary
#         article.save()
        
#         # حذف تگ‌های قبلی و اضافه کردن تگ‌های جدید
#         article.tags.clear()
#         for tag_name in new_tags:
#             tag, created = WikiTag.objects.get_or_create(
#                 title_fa=tag_name,
#                 defaults={
#                     'slug': tag_name.replace(' ', '-').replace('‌', '-')[:50],
#                     'title_en': tag_name
#                 }
#             )
#             article.tags.add(tag)
        
#         return JsonResponse({
#             'success': True,
#             'summary': new_summary,
#             'tags': new_tags,
#             'message': 'خلاصه و تگ‌ها با موفقیت تولید شدند'
#         })
        
#     except Exception as e:
#         return JsonResponse({
#             'error': f'خطا: {str(e)}'
#         }, status=500)

@csrf_exempt
def preview_ai_content(request):
    """پیش‌نمایش خلاصه"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        title = data.get('title', '')
        
        if not text:
            return JsonResponse({'error': 'متن مورد نیاز است'}, status=400)
        
        llm_service = FreeAIService()
        
        summary = llm_service.generate_summary(text)
        tags = llm_service.extract_tags(text, title)
        
        return JsonResponse({
            'success': True,
            'summary': summary,
            'tags': tags
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'خطا: {str(e)}'
        }, status=500)