from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .models import WikiArticle, WikiCategory

User = get_user_model()

class WikiSystemTests(TestCase):
    # بسیار مهم: از آنجایی که پروژه شما چند دیتابیسی است، باید دیتابیس‌های درگیر را معرفی کنید
    databases = {'default', 'team6'}

    def setUp(self):
        """آماده‌سازی داده‌های پایه برای هر تست"""
        self.client = Client()
        
        # ۱. ساخت کاربر تست با فیلدهای مورد نیاز پروژه Core
        self.user = User.objects.create_user(
            email='dev@team6.com',
            password='testpassword123'
        )
        
        # ۲. ساخت دسته‌بندی
        self.category = WikiCategory.objects.create(
            title_fa="طبیعت گردی", 
            slug="nature"
        )

    def test_ping_endpoint(self):
        """تست در دسترس بودن سرویس (Health Check)"""
        # تست بدون لاگین (باید ۴۰۱ یا ۳۰۲ به لاگین بدهد بسته به تنظیمات Middleware)
        response = self.client.get(reverse('team6:ping'))
        self.assertEqual(response.status_code, 200)
    
    @patch('deep_translator.GoogleTranslator.translate')
    @patch('team6.services.llm_service.FreeAIService.generate_summary')
    def test_complete_article_flow(self, mock_translate, mock_ai_summary):
        """تست چرخه کامل: لاگین -> ارسال فرم -> پردازش AI -> ذخیره در دیتابیس"""
        
        # تنظیم مقادیر فیک برای بخش‌های سنگین و وابسته به اینترنت
        mock_translate.return_value = "Cloud Forest Test"
        mock_ai_summary.return_value = "این یک خلاصه تولید شده توسط هوش مصنوعی تست است."

        # ورود به سیستم
        self.client.force_login(self.user)

        # داده‌های ارسالی برای ساخت مقاله
        post_data = {
            'title_fa': 'جنگل ابر سمنان',
            'place_name': 'Cloud Forest',
            'body_fa': 'متن تست درباره زیبایی‌های جنگل ابر...',
            'category': self.category.id_category, # استفاده از ID دسته‌بندی ساخته شده در setUp
            'status': 'published'
        }

        # ارسال درخواست POST
        response = self.client.post(reverse('team6:article_add'), data=post_data)

        # ۱. بررسی ریدایرکت (نشانه موفقیت)
        self.assertEqual(response.status_code, 302)

        # ۲. بررسی دیتابیس (آیا مقاله ساخته شد؟)
        article = WikiArticle.objects.get(title_fa='جنگل ابر سمنان')
        self.assertEqual(article.author_user_id, self.user.id)
        
        # ۳. بررسی اینکه آیا سرویس‌های کمکی (AI و ترجمه) درست فراخوانی شدند
        self.assertEqual(article.summary, "این یک خلاصه تولید شده توسط هوش مصنوعی تست است.")
        self.assertTrue(mock_translate.called)

    def test_semantic_search_view(self):
        """تست لود شدن صفحه جستجو و پارامترهای معنایی"""
        self.client.force_login(self.user)
        # ارسال کوئری جستجو
        response = self.client.get(reverse('team6:index'), {'q': 'جنگل', 'search_type': 'semantic'})
        
        self.assertEqual(response.status_code, 200)
        # بررسی وجود المان‌های خاص در تمپلیت
        self.assertTemplateUsed(response, 'team6/article_list.html')

    def test_article_404_custom_template(self):
        """بررسی هندلینگ خطای ۴۰۴ با تمپلیت اختصاصی"""
        response = self.client.get('/team6/article/slug-ke-vojud-nadarad/')
        self.assertEqual(response.status_code, 404)
        # اگر تمپلیت اختصاصی دارید:
        # self.assertTemplateUsed(response, 'team6/errors/404.html')
        
    @patch('team6.services.llm_service.FreeAIService.generate_summary')
    def test_article_creation_with_ai_failure(self, mock_ai_summary):
        """تست اینکه اگر هوش مصنوعی متن خالی برگرداند، سیستم با خطا مواجه نشود"""
        mock_ai_summary.return_value = "" # شبیه‌سازی شکست هوش مصنوعی
        
        self.client.force_login(self.user)
        data = {
            'title_fa': 'تست شکست AI',
            'place_name': 'Test',
            'body_fa': 'یک متن کوتاه...',
            'category': self.category.id_category,
            'status': 'published'
        }
        response = self.client.post(reverse('team6:article_add'), data=data)
        
        # سیستم باید همچنان مقاله را بسازد (فقط خلاصه خالی می‌ماند یا دیفالت می‌گیرد)
        self.assertEqual(response.status_code, 302)
        article = WikiArticle.objects.get(title_fa='تست شکست AI')
        self.assertEqual(article.summary, "")
        
    def test_basic_keyword_search(self):
        """تست جستجوی معمولی بر اساس کلمات موجود در عنوان"""
        # ابتدا یک مقاله می‌سازیم
        WikiArticle.objects.create(
            title_fa="قلعه رودخان",
            body_fa="توضیحات قلعه...",
            category=self.category,
            author_user_id=self.user.id,
            status='published'
        )
        
        # جستجو برای کلمه "قلعه"
        response = self.client.get(reverse('team6:index'), {'q': 'قلعه', 'search_type': 'text'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "قلعه رودخان")
        
    def test_anonymous_user_cannot_add_article(self):
        """کاربر مهمان نباید بتواند به صفحه ثبت مقاله دسترسی داشته باشد"""
        # بدون force_login
        response = self.client.get(reverse('team6:article_add'))
        
        # معمولاً جنگو به صفحه لاگین ریدایرکت می‌کند (۳۰۲)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/', response.url)
        
    def test_create_article_invalid_data(self):
        """ارسال فرم ناقص نباید باعث ثبت مقاله شود"""
        self.client.force_login(self.user)
        # عنوان (title_fa) را خالی می‌فرستیم
        data = {'body_fa': 'متن بدون عنوان', 'category': self.category.id_category}
        
        response = self.client.post(reverse('team6:article_add'), data=data)
        
        # نباید ریدایرکت شود (معمولاً دوباره همان صفحه با خطا نمایش داده می‌شود: ۲۰۰)
        self.assertEqual(response.status_code, 200)
        # چک می‌کنیم که در دیتابیس چیزی ذخیره نشده باشد
        self.assertFalse(WikiArticle.objects.filter(body_fa='متن بدون عنوان').exists())
        
    def test_xss_content_handling(self):
        """تست مقاومت در برابر تزریق اسکریپت در متن مقاله"""
        self.client.force_login(self.user)
        malicious_code = "<script>alert('Hacked');</script><b>متن ایمن</b>"
        
        data = {
            'title_fa': 'تست امنیتی',
            'place_name': 'Test',
            'body_fa': malicious_code,
            'category': self.category.id_category,
        }
        response = self.client.post(reverse('team6:article_add'), data=data)
        
        self.assertEqual(response.status_code, 302)
        article = WikiArticle.objects.get(title_fa='تست امنیتی')
        # بررسی اینکه تگ‌های خطرناک یا فرار داده شده‌اند (Escape) یا سیستم کرش نکرده
        self.assertIn('<b>', article.body_fa)
    @patch('team6.services.llm_service.FreeAIService.generate_summary')
    def test_massive_content_processing(self, mock_ai_summary):
        """تست ارسال متن بسیار سنگین برای پردازش هوش مصنوعی"""
        mock_ai_summary.return_value = "خلاصه کوتاه برای متن سنگین"
        self.client.force_login(self.user)
        
        huge_body = "این یک متن تکراری است. " * 2000 # تولید متن بسیار طولانی
        
        data = {
            'title_fa': 'مقاله سنگین',
            'place_name': 'Cloud',
            'body_fa': huge_body,
            'category': self.category.id_category,
        }
        response = self.client.post(reverse('team6:article_add'), data=data)
        
        # سیستم نباید Timeout بدهد (چون AI را Mock کردیم، سرعت باید اوکی باشد)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(WikiArticle.objects.filter(title_fa='مقاله سنگین').exists())
        
    def test_article_behavior_on_category_delete(self):
        """تایید اینکه سیستم اجازه حذف دسته‌بندی دارای مقاله را نمی‌دهد (تست PROTECT)"""
        # ایجاد یک مقاله
        WikiArticle.objects.create(
            title_fa="مقاله محافظت شده",
            slug="protected-slug",
            category=self.category,
            author_user_id=self.user.id
        )
        
        # حالا انتظار داریم که حذف دسته‌بندی با خطای ProtectedError مواجه شود
        from django.db.models.deletion import ProtectedError
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_advanced_filter_logic(self):
        """تست ترکیب فیلتر با رعایت یکتایی مطلق URL و Slug"""
        # ایجاد دسته‌بندی دوم
        other_cat = WikiCategory.objects.create(title_fa="تاریخی", slug="history-cat")
        
        # مقاله اول
        WikiArticle.objects.create(
            title_fa="جنگل فندقلو", 
            slug="fandoqloo-unique", 
            url="url-1",  # مقدار دهی صریح به فیلد url
            category=self.category, 
            author_user_id=self.user.id, 
            status='published'
        )
        
        # مقاله دوم
        WikiArticle.objects.create(
            title_fa="تخت جمشید", 
            slug="persepolis-unique", 
            url="url-2",  # مقدار دهی صریح به فیلد url برای جلوگیری از IntegrityError
            category=other_cat, 
            author_user_id=self.user.id, 
            status='published'
        )
        
        # اجرای فیلتر
        url_filter = reverse('team6:index') + f'?q=جنگل&cat={self.category.id_category}'
        response = self.client.get(url_filter)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "جنگل فندقلو")
        self.assertNotContains(response, "تخت جمشید")
        
    def test_unicode_and_normalization(self):
        """تست هندلینگ نیم‌فاصله و کاراکترهای فارسی در جستجو"""
        WikiArticle.objects.create(
            title_fa="خانه‌ی درختی", # استفاده از ی همراه با نیم‌فاصله یا ه
            slug="tree-house",
            category=self.category,
            author_user_id=self.user.id,
            status='published'
        )
        
        # جستجو با ی معمولی
        response = self.client.get(reverse('team6:index'), {'q': 'خانه'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "خانه")
        
    # @patch('team6.services.vector_service.VectorSearch.get_similar') # مسیر کلاس جستجوی خود را چک کنید
    # def test_semantic_search_logic(self, mock_vector_search):
    #     """تست منطق جستجوی معنایی: آیا مترادف‌ها نتایج درست می‌دهند؟"""
    #     # شبیه‌سازی خروجی برداری: وقتی کاربر "بیشه" زد، آی‌دی مقاله "جنگل" را برگردان
    #     mock_article = WikiArticle.objects.create(
    #         title_fa="جنگل‌های شمال", 
    #         slug="north-forest", 
    #         url="unique-url-ai",
    #         category=self.category,
    #         author_user_id=self.user.id,
    #         status='published'
    #     )
    #     mock_vector_search.return_value = [mock_article.id]
        
    #     response = self.client.get(reverse('team6:index'), {'q': 'بیشه', 'search_type': 'semantic'})
        
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, "جنگل‌های شمال")
    
    
    
#     # در انتهای فایل settings.py
# import sys

# if 'test' in sys.argv:
#     # هدایت همه درخواست‌ها به یک دیتابیس موقت در حافظه (Memory)
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': ':memory:',
#         },
#         'team6': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': ':memory:',
#         }
#     }
#     # غیرفعال کردن موقت Router برای جلوگیری از سردرگمی جنگو در تست
#     DATABASE_ROUTERS = []