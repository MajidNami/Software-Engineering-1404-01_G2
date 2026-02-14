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
from django.db import IntegrityError
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .services.llm_service import FreeAIService
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from django.http import Http404
from .services.semantic_search import SemanticSearchService
from bs4 import BeautifulSoup
from .models import WikiArticle, WikiArticleLink
from django.utils.text import slugify
from .models import ArticleFollow, ArticleNotification
import numpy as np
from django.db.models import F
from django.utils.timezone import now
def sync_internal_links(article):
    """
    این تابع متن مقاله را اسکن کرده و لینک‌های داخلی را استخراج و در دیتابیس ذخیره می‌کند.
    """
    # ۱. حذف لینک‌های قدیمی این مقاله برای بازنویسی
    WikiArticleLink.objects.filter(from_article=article).delete()

    # ۲. پارس کردن متن HTML مقاله
    soup = BeautifulSoup(article.body_fa, 'html.parser')
    
    # ۳. پیدا کردن تمام تگ‌های <a>
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        
        # بررسی اینکه آیا لینک مربوط به سیستم خودمان است
        if '/team6/article/' in href:
            # استخراج اسلاگ از انتهای آدرس
            # مثال: /team6/article/si-o-se-pol/ -> si-o-se-pol
            target_slug = href.strip('/').split('/')[-1]
            
            try:
                target_article = WikiArticle.objects.get(slug=target_slug)
                # ذخیره در جدول پیوندها
                WikiArticleLink.objects.get_or_create(
                    from_article=article,
                    to_article=target_article,
                    defaults={'anchor_text': a_tag.get_text()}
                )
            except WikiArticle.DoesNotExist:
                # اگر مقاله‌ای با این اسلاگ پیدا نشد، از آن عبور کن
                continue

# تنظیم لاگر برای چاپ در ترمینال
logger = logging.getLogger(__name__)


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
        # queryset = WikiArticle.objects.filter(status='published')
        # q = self.request.GET.get('q')
        
        # search_type = self.request.GET.get('search_type', 'direct')

        # if q:  # جستجوی مستقیم یا معنایی
        #     if search_type == 'semantic':
        #         queryset = queryset.filter(
        #             Q(title_fa__icontains=q) | 
        #             Q(body_fa__icontains=q) |
        #             Q(summary__icontains=q)
        #         ).distinct()
        #     else:  # جستجوی مستقیم
        #         queryset = queryset.filter(
        #             Q(title_fa__icontains=q) | 
        #             Q(body_fa__icontains=q)
        #         )
        queryset = WikiArticle.objects.filter(status='published')

        q = self.request.GET.get('q')
        search_type = self.request.GET.get('search_type', 'direct')
        
        cat = self.request.GET.getlist('category')
        if cat:
            queryset = queryset.filter(category__slug__in=cat)
        # ---------- سرچ معنایی ----------
        if q and search_type == 'semantic':
            articles = list(queryset)

            if not articles:
                return queryset.none()

            semantic_service = SemanticSearchService()

            ranked_articles = semantic_service.search(
                articles=articles,
                query=q,
                k=10
            )

            # فقط خود مقاله‌ها به ترتیب شباهت معنایی
            return [article for article, score in ranked_articles]
            all_articles = list(queryset)
            if not all_articles:
                return queryset.none()

            # ۱. آماده‌سازی متن مقالات (Corpus)
            corpus = []
            for art in all_articles:
                # ترکیب فیلدها برای جستجوی دقیق‌تر
                combined_text = f"{art.place_name or ''} {art.title_fa} {art.summary or ''} {art.body_fa}"
                corpus.append(combined_text)

            # ۲. اضافه کردن کوئری کاربر به انتهای لیست برای بردارسازی
            corpus.append(q)

            # ۳. تبدیل متون به بردار (Vectorization)
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(corpus)

            # ۴. محاسبه شباهت کسینوسی کوئری (آخرین عنصر) با تک‌تک مقالات
            # خروجی یک لیست از اعداد بین 0 و 1 است
            cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])[0]

            # ۵. فیلتر کردن بر اساس حد آستانه (Threshold)
            # عدد 0.1 معمولاً مناسب است؛ اگر نتایج خیلی بی‌ربط هستند عدد را بزرگتر کن (مثلاً 0.15)
            THRESHOLD = 0.1 
            
            scored_articles = []
            for idx, score in enumerate(cosine_sim):
                if score >= THRESHOLD:
                    scored_articles.append({
                        'article': all_articles[idx],
                        'score': score
                    })

            # ۶. مرتب‌سازی نتایج بر اساس امتیاز (نزولی)
            scored_articles.sort(key=lambda x: x['score'], reverse=True)

            # ۷. استخراج مقالات نهایی برای نمایش
            final_list = [item['article'] for item in scored_articles]
            
            # برگرداندن نتایج فیلتر شده و مرتب شده
            return final_list
            # ---------- سرچ مستقیم ----------
        if q:
            queryset = queryset.filter(
                Q(title_fa__icontains=q) |
                Q(body_fa__icontains=q)
            )

        # return queryset
            
        sort = self.request.GET.get('sort', 'alphabetical')
        if sort == 'newest':
            queryset = queryset.order_by('-published_at')
        # elif sort == 'followers':
        #     queryset = queryset.order_by('-follower_count')
        elif sort == 'views':
            queryset = queryset.order_by('-view_count')
        else:
            queryset = queryset.order_by('title_fa')
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = WikiCategory.objects.all()
        return context

# ایجاد مقاله
class ArticleCreateView(CreateView):
    model = WikiArticle
    template_name = 'team6/article_form.html'
    fields = ['title_fa', 'place_name', 'body_fa', 'summary', 'featured_image_url']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "برای ایجاد مقاله باید وارد سیستم شوید.")
            return redirect('/auth/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        article = form.save(commit=False)

        article.author_user_id = self.request.user.id
        article.last_editor_user_id = self.request.user.id
        # article.status = 'published'
        if 'save_draft' in self.request.POST:
            article.status = 'draft'
        else:
            article.status = 'published'
            article.published_at = now()

        featured_image = self.request.POST.get('featured_image_url', '')
        if featured_image and featured_image.lower() in ['none', 'null', '']:
            article.featured_image_url = None  # یا ''
        else:
            article.featured_image_url = featured_image    

        # دسته‌بندی
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

        # --- اصلاح بخش اسلاگ ---
        # اولویت با نام مکان، اگر نبود عنوان فارسی
        slug_source = article.place_name if article.place_name else article.title_fa
        title_slug = slugify(slug_source, allow_unicode=True) # allow_unicode=True برای فارسی
        
        if not title_slug or WikiArticle.objects.filter(slug=title_slug).exists():
            # اگر اسلاگ تکراری بود یا ساخته نشد، یک کد رندوم اضافه کن
            article.slug = f"{title_slug}-{str(uuid.uuid4())[:8]}" if title_slug else str(uuid.uuid4())[:12]
        else:
            article.slug = title_slug
            
        article.url = f"/team6/article/{article.slug}/"
        # ترجمه انگلیسی
        try:
            article.title_en = GoogleTranslator(source='fa', target='en').translate(article.title_fa)
            article.body_en = GoogleTranslator(source='fa', target='en').translate(article.body_fa)
        except Exception:
            article.title_en = article.title_fa
            article.body_en = article.body_fa

        # تولید خلاصه و تگ با AI
        if not article.summary or not article.summary.strip():
            try:
                llm = FreeAIService()
                
                # 1️⃣ خلاصه انگلیسی
                summary_en = llm.generate_summary(article.body_en)
                
                # 2️⃣ ترجمه خلاصه به فارسی
                try:
                    article.summary = GoogleTranslator(source='en', target='fa').translate(summary_en)
                except Exception:
                    article.summary = summary_en  # اگر ترجمه خراب شد، همان انگلیسی ذخیره شود
                
                # خلاصه را زودتر ذخیره می‌کنیم تا در صورت خطا در مراحل تگ‌گذاری، نتیجه خلاصه از دست نرود.
                article.save(update_fields=['summary'])

                # تگ‌های کاربر
                user_tags_input = self.request.POST.get('tags', '')
                user_tags = [t.strip() for t in user_tags_input.split(",") if t.strip()]

                # تگ‌های AI
                ai_tags = llm.extract_tags(article.body_fa, article.title_fa)

                # ترکیب بدون تکرار
                all_tags = set(user_tags + ai_tags)

                for tag_name in all_tags:
                    tag_qs = WikiTag.objects.filter(title_fa=tag_name)
                    if tag_qs.exists():
                        tag = tag_qs.first()
                    else:
                        tag = WikiTag.objects.create(title_fa=tag_name)
                    article.tags.add(tag)


            except Exception as e:
                messages.error(self.request, f"خطا در تولید AI: {e}")
                return self.form_invalid(form)

        article.save()

        # لینک داخلی و تاریخچه
        sync_internal_links(article)
        WikiArticleRevision.objects.create(
            article=article,
            revision_no=1,
            body_fa=article.body_fa,
            body_en=article.body_en,
            editor_user_id=self.request.user.id,
            change_note="ایجاد اولیه مقاله"
        )

        messages.success(self.request, f"✅ مقاله '{article.title_fa}' با موفقیت ایجاد شد!")
        return redirect('team6:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = WikiCategory.objects.all()
        context['all_articles'] = WikiArticle.objects.filter(status='published').values('title_fa', 'slug')
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
    try:
        if request.method == "POST":
            # ۱. دریافت مقادیر جدید از فرم
            new_body = request.POST.get('body_fa', article.body_fa)
            new_title = request.POST.get('title_fa', article.title_fa)
            new_summary = request.POST.get('summary', article.summary)
            change_note = request.POST.get('change_note', 'ویرایش محتوا')

            # ۲. محاسبه شماره نسخه جدید (تعداد فعلی + ۱)
            new_rev_no = WikiArticleRevision.objects.filter(article=article).count() + 1
            
            # ۳. ایجاد رکورد جدید در تاریخچه (ذخیره نسخه جدید)
            WikiArticleRevision.objects.create(
                article=article,
                revision_no=new_rev_no,
                body_fa=new_body,
                editor_user_id=request.user.id,
                change_note=change_note
            )

            # ۴. آپدیت مقاله اصلی
            is_published = 'save_published' in request.POST
            if is_published:
                article.status = 'published'
                if not article.published_at:
                    article.published_at = now()
                success_msg = "✅ مقاله با موفقیت منتشر و نسخه جدید ذخیره شد."
            else:
                article.status = 'draft'
                success_msg = "💾 تغییرات در پیش‌نویس ذخیره شد (نسخه جدید ثبت شد)."

            article.title_fa = new_title
            article.body_fa = new_body
            article.summary = new_summary
            article.current_revision_no = new_rev_no
            article.last_editor_user_id = request.user.id
            
            # عکس و دسته‌بندی
            article.featured_image_url = request.POST.get('featured_image_url', article.featured_image_url)
            category_id = request.POST.get('category')
            if category_id:
                article.category = WikiCategory.objects.get(id_category=category_id)

            # ۵. تگ‌ها
            tags_input = request.POST.get('tags', None)
            if tags_input is not None:
                tag_names = [t.strip() for t in tags_input.split(",") if t.strip()]
                article.tags.set([])
                for name in tag_names:
                    tag, _ = WikiTag.objects.get_or_create(
                        title_fa=name,
                        defaults={'slug': slugify(name, allow_unicode=True), 'title_en': name}
                    )
                    article.tags.add(tag)

            article.save()
            sync_internal_links(article)

            messages.success(request, "✅ مقاله با موفقیت ویرایش شد")
            if article.status == 'published':
                return redirect('team6:article_detail', slug=article.slug)
            else:
                return redirect('team6:draft_list')
    except Exception as e:
            # اگر خطایی رخ داد، چاپ کن تا در ترمینال ببینی
            print(f"❌ Error in edit_article: {e}")
            messages.error(request, f"خطایی رخ داد: {e}")
            # بازگشت به همان صفحه ویرایش به جای ارور ۵۰۰
            return redirect('team6:edit_article', slug=article.slug)
    # برای GET
    current_rev_display = WikiArticleRevision.objects.filter(article=article).count() + 1
    categories = WikiCategory.objects.all()
    all_articles = WikiArticle.objects.filter(status='published')
    
    return render(request, 'team6/article_edit.html', {
        'article': article,
        'current_rev': current_rev_display,
        'categories': categories,
        'all_articles': all_articles,
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
    try:
        article = get_object_or_404(WikiArticle, slug=slug)
        revisions = WikiArticleRevision.objects.filter(article=article).order_by('-revision_no')
        return render(request, 'team6/article_revisions.html', {
            'article': article, 
            'revisions': revisions
        })
    except Exception as e:
        import traceback
        print("--- ERROR START ---")
        print(traceback.format_exc()) # این تمام جزئیات خطا را چاپ می‌کند
        print("--- ERROR END ---")
        raise e
# نمایش جزئیات مقاله
def article_detail(request, slug):
    try:
        article = get_object_or_404(WikiArticle, slug=slug)
        
        # گرفتن لیست مقالات دیده شده در این سشن (اگر نبود، لیست خالی)
        viewed_articles = request.session.get('viewed_articles', [])
        
        # افزایش بازدید
        #  چک کردن اینکه آیا این مقاله خاص قبلاً توسط این یوزر دیده شده یا نه
        # جلوگیری از شمردن چندباره بازدید در یک نشست (session) برای همان مقاله
        if slug not in viewed_articles:
            # if hasattr(article, 'view_count'):
                # article.view_count += 1
                # # استفاده از update_fields برای امنیت و سرعت بیشتر دیتابیس
                # article.save(update_fields=['view_count'])
            # افزایش بازدید در دیتابیس
            WikiArticle.objects.filter(pk=article.pk).update(view_count=F('view_count') + 1)
            
            # تازه کردن آبجکت برای نمایش در تمپلت
            article.refresh_from_db()
        #  اضافه کردن اسلاگ این مقاله به لیست دیده‌شده‌های یوزر
            viewed_articles.append(slug)
            request.session['viewed_articles'] = viewed_articles
            # اطلاع به جنگو که سشن تغییر کرده و باید ذخیره شود
            request.session.modified = True
        return render(request, 'team6/article_detail.html', {'article': article})
    except WikiArticle.DoesNotExist:
        logger.error(f"❌ Article NOT FOUND: slug='{slug}'")
        return render(request, 'team6/errors/404.html', {
            'error_message': f"متأسفانه مقاله‌ای با آدرس '{slug}' پیدا نشد."
        }, status=404)
    except Http404:
        logger.error(f"❌  NOT FOUND: slug='{slug}'")
        return render(request, 'team6/errors/404.html', {
            'error_message': "پیدا نشد."
        }, status=404)
    except Exception as e:
        logger.exception(f"🔥 Critical Error in article_detail: {e}")
        return render(request, 'team6/errors/500.html', {
            'error_message': "یک خطای فنی در سرور رخ داده است. تیم فنی مطلع شد."
        }, status=500)

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
    print("Received request for wiki content with params:", request.GET)
    place_query = request.GET.get('place', None)
    if not place_query:
        return JsonResponse({"error": "پارامتر place الزامی است"}, status=400)

    # ۱. تلاش برای پیدا کردن تطابق دقیق (Exact Match)
    # ابتدا در place_name و سپس در slug
    exact_match = WikiArticle.objects.filter(
        status='published'
    ).filter(
        Q(place_name__iexact=place_query) | 
        Q(slug__iexact=place_query) |
        Q(title_fa__iexact=place_query)
    )

    if exact_match.exists():
        # return JsonResponse(serialize_article(exact_match), json_dumps_params={'ensure_ascii': False})
        best_exact = max(exact_match, key=lambda x: calculate_article_score(x))
        return JsonResponse(serialize_article(best_exact), json_dumps_params={'ensure_ascii': False})

    # ۲. اگر تطابق دقیق پیدا نشد: استفاده از TF-IDF و Cosine Similarity
    all_articles = list(WikiArticle.objects.filter(status='published'))
    
    if not all_articles:
        return JsonResponse({"message": "هیچ مقاله‌ای در سیستم موجود نیست"}, status=404)

    # ساختن بدنه متن برای بردارسازی (ترکیب عنوان، نام مکان و خلاصه)
    corpus = []
    for art in all_articles:
        combined_text = f"{art.place_name or ''} {art.title_fa} {art.summary or ''} {art.body_fa[:200]}"
        corpus.append(combined_text)

    # اضافه کردن کوئری کاربر به انتهای لیست برای بردارسازی همزمان
    corpus.append(place_query)

    # بردارسازی
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # محاسبه شباهت کسینوسی بین "آخرین عنصر" (کوئری) و بقیه (مقالات)
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    
    # پیدا کردن ایندکس بهترین شباهت
    best_index = np.argmax(cosine_sim)
    max_similarity = cosine_sim[0][best_index]

    # تعیین یک حد آستانه (Threshold) برای جلوگیری از نتایج کاملاً بی‌ربط
    if max_similarity < -1: # این عدد را می‌توانی با تست‌های بیشتر تنظیم کنید
        return JsonResponse({"message": "محتوایی با شباهت کافی یافت نشد"}, status=404)

    best_article = all_articles[best_index]
    return JsonResponse(serialize_article(best_article), json_dumps_params={'ensure_ascii': False})


def serialize_article(article):
    """تابع کمکی برای تبدیل مدل به فرمت JSON مورد توافق"""
    return {
        "category": article.category.title_fa if article.category else "تاریخی",
        "tags": list(article.tags.values_list('title_fa', flat=True)),
        "summary": article.summary or "",
        "description": article.body_fa,
        "images": [article.featured_image_url] if article.featured_image_url else [],
        "url": article.url,
        "updated_at": article.updated_at.isoformat()
    }


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

@login_required
def follow_article(request, slug):
    """دنبال کردن/لغو دنبال کردن مقاله"""
    article = get_object_or_404(WikiArticle, slug=slug)
    
    if request.method == "POST":
        action = request.POST.get('action', 'follow')
        
        if action == 'follow':
            # بررسی آیا قبلاً دنبال کرده یا نه
            follow, created = ArticleFollow.objects.get_or_create(
                user_id=request.user.id,
                article=article,
                defaults={'notify': True}
            )
            
            if created:
                messages.success(request, f"✅ مقاله '{article.title_fa}' با موفقیت دنبال شد.")
            else:
                follow.notify = True
                follow.save()
                messages.info(request, f"✅ اعلان‌های مقاله '{article.title_fa}' فعال شد.")
                
        elif action == 'unfollow':
            ArticleFollow.objects.filter(
                user_id=request.user.id,
                article=article
            ).delete()
            messages.success(request, f"✅ دنبال‌کردن مقاله '{article.title_fa}' لغو شد.")
        
        return redirect('team6:article_detail', slug=slug)
    
    # برای GET درخواست
    is_following = ArticleFollow.objects.filter(
        user_id=request.user.id,
        article=article
    ).exists()
    
    return JsonResponse({
        'is_following': is_following,
        'article_title': article.title_fa
    })

@login_required
def toggle_notification(request, slug):
    article = get_object_or_404(WikiArticle, slug=slug)

    follow, created = ArticleFollow.objects.get_or_create(
        user_id=request.user.id,
        article=article,
        defaults={'notify': True}
    )

    if not created:
        follow.notify = not follow.notify
        follow.save()

    status = "فعال" if follow.notify else "غیرفعال"
    messages.success(
        request,
        f"🔔 اعلان‌های مقاله «{article.title_fa}» {status} شد."
    )

    return redirect('team6:article_detail', slug=slug)


@login_required
def notifications_list(request):
    """لیست اعلان‌های کاربر"""
    notifications = ArticleNotification.objects.filter(
        user_id=request.user.id,
        is_active=True
    ).order_by('-created_at').select_related('article')
    
    return render(request, 'team6/notifications_list.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request, notification_id):
    """علامت‌گذاری اعلان به عنوان خوانده شده"""
    try:
        notification = ArticleNotification.objects.get(
            id=notification_id,
            user_id=request.user.id
        )
        notification.is_read = True
        notification.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
            
    except ArticleNotification.DoesNotExist:
        pass
    
    return redirect('team6:notifications_list')

@login_required
def archive_notification(request, notification_id):
    """آرشیو کردن اعلان"""
    try:
        notification = ArticleNotification.objects.get(
            id=notification_id,
            user_id=request.user.id
        )
        notification.is_active = False
        notification.save()
        
        messages.success(request, "اعلان آرشیو شد.")
    except ArticleNotification.DoesNotExist:
        messages.error(request, "اعلان پیدا نشد.")
    
    return redirect('team6:notifications_list')

@login_required
def mark_all_read(request):
    """علامت‌گذاری همه اعلان‌ها به عنوان خوانده شده"""
    ArticleNotification.objects.filter(
        user_id=request.user.id,
        is_read=False,
        is_active=True
    ).update(is_read=True)
    
    messages.success(request, "همه اعلان‌ها خوانده شدند.")
    return redirect('team6:notifications_list')
@login_required
def archive_all_notifications(request):
    """آرشیو کردن همه اعلان‌های کاربر"""
    try:
        # آرشیو کردن همه اعلان‌های فعال کاربر
        updated_count = ArticleNotification.objects.filter(
            user_id=request.user.id,
            is_active=True
        ).update(is_active=False)
        
        messages.success(request, f"✅ همه اعلان‌ها ({updated_count} عدد) آرشیو شدند.")
        
    except Exception as e:
        messages.error(request, f"خطا در آرشیو کردن اعلان‌ها: {e}")
    
    return redirect('team6:notifications_list')

@login_required
def rollback_revision(request, slug, revision_no):
    article = get_object_or_404(WikiArticle, slug=slug)
    # پیدا کردن نسخه‌ای که قرار است به آن برگردیم
    target_revision = get_object_or_404(WikiArticleRevision, article=article, revision_no=revision_no)
    
    if request.method == "POST":
        # ۱. محاسبه شماره نسخه جدید برای عملیات بازگردانی
        new_rev_num = WikiArticleRevision.objects.filter(article=article).count() + 1
        
        # ۲. آپدیت مقاله اصلی
        article.body_fa = target_revision.body_fa
        article.current_revision_no = new_rev_num
        article.last_editor_user_id = request.user.id
        article.save()
        
        # ۳. ثبت این "بازگردانی" به عنوان یک نسخه جدید در تاریخچه
        WikiArticleRevision.objects.create(
            article=article,
            revision_no=new_rev_num,
            body_fa=target_revision.body_fa,
            editor_user_id=request.user.id,
            change_note=f"⏪ بازگردانی به نسخه شماره {revision_no}"
        )
        
        messages.success(request, f"✅ مقاله با موفقیت به نسخه {revision_no} بازگردانی شد.")
        return redirect('team6:article_detail', slug=article.slug)
    
    # اگر متد GET بود، به صفحه تایید برود (اگر فایلی به نام rollback_confirm داری)
    return render(request, 'team6/rollback_confirm.html', {'article': article, 'revision': target_revision})

@login_required
def draft_list(request):
    # فقط مقالاتی که وضعیت پیش‌نویس دارند و نویسنده‌شان کاربر فعلی است
    drafts = WikiArticle.objects.filter(
        status='draft', 
        author_user_id=request.user.id
    ).order_by('-updated_at')
    
    return render(request, 'team6/draft_list.html', {'drafts': drafts})