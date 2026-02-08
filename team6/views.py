from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import uuid
from django.contrib import messages
from django.utils.text import slugify
from .models import WikiArticle, WikiCategory, WikiArticleRevision, WikiArticleReports
from deep_translator import GoogleTranslator
import requests

TEAM_NAME = "team6"

# --- Base views ---
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    articles = WikiArticle.objects.filter(status='published')
    return render(request, "team6/index.html", {"articles": articles})

# لیست مقالات
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
        article.summary = summarize_text(article.body_fa)
        # ذخیره مقاله
        article.save()
        
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
    
    # این متغیر را باید از خود مقاله بگیریم
    current_rev = article.current_revision_no if hasattr(article, 'current_revision_no') else 1

    if request.method == "POST":
        # ذخیره نسخه قبلی در تاریخچه
        WikiArticleRevision.objects.create(
            article=article,
            revision_no=current_rev,
            body_fa=article.body_fa,
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
        
        article.current_revision_no = current_rev + 1
        article.last_editor_user_id = request.user.id
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
def report_article(request, slug):
    if not request.user.is_authenticated:
        return redirect('/auth/')
    
    article = get_object_or_404(WikiArticle, slug=slug)
    
    if request.method == "POST":
        reporter_id = request.user.id 
        
        WikiArticleReports.objects.create(
            article=article,
            reporter_user_id=reporter_id,
            report_type=request.POST.get('type', 'other'),
            description=request.POST.get('desc', '')
        )
        return render(request, 'team6/report_success.html', {'article': article})
    
    return render(request, 'team6/article_report.html', {'article': article})

# نمایش نسخه‌ها
def article_revisions(request, slug):
    article = get_object_or_404(WikiArticle, slug=slug)
    revisions = WikiArticleRevision.objects.filter(article=article).order_by('-created_at')
    return render(request, 'team6/article_revisions.html', {
        'article': article, 
        'revisions': revisions
    })

# نمایش جزئیات مقاله
def article_detail(request, slug):
    article = get_object_or_404(WikiArticle, slug=slug)
    
    # افزایش بازدید
    if hasattr(article, 'view_count'):
        article.view_count += 1
        article.save()
    
    return render(request, 'team6/article_detail.html', {'article': article})

# API برای محتوای ویکی
def get_wiki_content(request):
    place_query = request.GET.get('place', None)
    
    if not place_query:
        return JsonResponse({"error": "پارامتر place الزامی است"}, status=400)
    
    # جستجو بر اساس نام مکان یا عنوان
    article = WikiArticle.objects.filter(
        Q(place_name__icontains=place_query) | 
        Q(title_fa__icontains=place_query)
    ).first()

    if not article:
        return JsonResponse({"message": "محتوایی برای این مکان یافت نشد"}, status=404)

    # ساخت خروجی
    data = {
        "id": str(article.id) if hasattr(article, 'id') else str(article.slug),
        "title": article.title_fa,
        "place_name": article.place_name,
        "category": article.category.title_fa if article.category else "",
        "tags": list(article.tags.values_list('title_fa', flat=True)) if hasattr(article, 'tags') else [],
        "summary": article.summary if hasattr(article, 'summary') else "",
        "description": article.body_fa,
        "url": f"/team6/article/{article.slug}/",
        "updated_at": article.updated_at.isoformat() if hasattr(article, 'updated_at') else ""
    }
    
    # اضافه کردن تصویر اگر وجود دارد
    if hasattr(article, 'featured_image_url') and article.featured_image_url:
        data["images"] = [article.featured_image_url]
    
    return JsonResponse(data)

def summarize_text(text):
    """
    این تابع متن فارسی رو می‌گیره و خلاصه‌شده‌ش رو برمی‌گردونه.
    از HuggingFace Inference API برای مدل‌های summarization استفاده می‌کنه.
    """
    API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"
    headers = {"Authorization": "Bearer hf_your_token_here"}  # اگر token لازم باشه

    payload = {
        "inputs": text,
        "parameters": {"min_length": 30, "max_length": 150}
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "summary_text" in result[0]:
            return result[0]["summary_text"]
        elif isinstance(result, dict) and "summary_text" in result:
            return result["summary_text"]
    except Exception as e:
        print("Error in summarization:", e)

    # اگر خلاصه‌سازی موفق نبود، متن کامل را برمی‌گردانیم
    return text[:150] + "..." if len(text) > 150 else text