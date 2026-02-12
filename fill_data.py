# import os
# import django
# import uuid
# import re
# from django.utils.text import slugify
# from django.utils.timezone import now
# from deep_translator import GoogleTranslator

# # ۱. تنظیمات اولیه جنگو
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
# django.setup()

# import wikipediaapi
# from team6.models import (
#     WikiArticle, WikiCategory, WikiTag,
#     WikiArticleLink, WikiArticleRef, WikiArticleRevision
# )


# def run_advanced_seeder():
#     wiki_fa = wikipediaapi.Wikipedia(
#         user_agent='IsfahanFullProject/1.0 (contact: your@email.com)',
#         language='fa'
#     )

#     isfahan_categories = {
#         "استان اصفهان": {"title": "استان اصفهان", "parent": None},
#         "شهرهای استان اصفهان": {"title": "شهرها و بخش‌ها", "parent": "استان اصفهان"},
#         "روستاهای استان اصفهان": {"title": "روستاها", "parent": "استان اصفهان"},
#         "آثار تاریخی استان اصفهان": {"title": "آثار تاریخی و ملی", "parent": "استان اصفهان"},
#         "جاذبه‌های گردشگری اصفهان": {"title": "گردشگری و طبیعت", "parent": "استان اصفهان"},
#         "عمارت‌های تاریخی استان اصفهان": {"title": "بناها و عمارت‌ها", "parent": "آثار تاریخی استان اصفهان"},
#         "باغ‌های استان اصفهان": {"title": "باغ‌ها و تفرجگاه‌ها", "parent": "جاذبه‌های گردشگری اصفهان"},
#     }

#     print("🚀 شروع فرآیند استخراج داده...")

#     processed_articles = {}

#     for wiki_cat_name, info in isfahan_categories.items():

#         parent_obj = None
#         if info['parent']:
#             parent_obj = WikiCategory.objects.using('team6').filter(
#                 slug=slugify(info['parent'], allow_unicode=True)
#             ).first()

#         db_cat, _ = WikiCategory.objects.using('team6').get_or_create(
#             slug=slugify(wiki_cat_name, allow_unicode=True),
#             defaults={'title_fa': info['title'], 'parent': parent_obj}
#         )

#         cat_page = wiki_fa.page(f"Category:{wiki_cat_name}")
#         if not cat_page.exists():
#             continue

#         members = [
#             p for p in cat_page.categorymembers.values()
#             if p.ns == wikipediaapi.Namespace.MAIN
#         ][:15]

#         for page in members:
#             try:
#                 en_title = page.langlinks['en'].title if 'en' in page.langlinks else None

#                 article, created = WikiArticle.objects.using('team6').update_or_create(
#                     url=page.fullurl,
#                     defaults={
#                         'place_name': page.title,
#                         'slug': slugify(page.title, allow_unicode=True)[:50],
#                         'title_fa': page.title,
#                         'title_en': en_title,
#                         'body_fa': page.text,
#                         'summary': page.summary[:1000],
#                         'category': db_cat,
#                         'status': 'published',
#                         'published_at': now(),
#                         'view_count': 0
#                     }
#                 )

#                 # ✅ ترجمه فقط اگر وجود نداشته باشد
#                 updated_fields = []

#                 if not article.title_en:
#                     try:
#                         article.title_en = GoogleTranslator(
#                             source='fa', target='en'
#                         ).translate(article.title_fa)
#                     except Exception:
#                         article.title_en = article.title_fa
#                     updated_fields.append('title_en')

#                 if not article.body_en:
#                     try:
#                         article.body_en = GoogleTranslator(
#                             source='fa', target='en'
#                         ).translate(article.body_fa[:4000])  # محدودیت طول
#                     except Exception:
#                         article.body_en = article.body_fa
#                     updated_fields.append('body_en')

#                 if updated_fields:
#                     article.save(using='team6', update_fields=updated_fields)

#                 processed_articles[page.title] = article

#                 # ✅ ساخت نسخه اولیه اگر وجود نداشت
#                 WikiArticleRevision.objects.using('team6').get_or_create(
#                     article=article,
#                     revision_no=1,
#                     defaults={
#                         'body_fa': page.text,
#                         'change_note': 'Initial import from Wikipedia'
#                     }
#                 )

#                 print(f"✅ پردازش شد: {page.title}")

#             except Exception as e:
#                 print(f"❌ خطا در پردازش {page.title}: {e}")

#     print("🎉 فرآیند با موفقیت پایان یافت.")


# if __name__ == "__main__":
#     run_advanced_seeder()


import os
import django
import requests
from django.utils.text import slugify
from django.utils.timezone import now
from deep_translator import GoogleTranslator

# ۱. تنظیمات اولیه جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
django.setup()

import wikipediaapi
from team6.models import WikiArticle, WikiCategory, WikiArticleRevision

def get_wiki_image(page_title):
    """استخراج آدرس تصویر اصلی مقاله از API ویکی‌پدیا"""
    try:
        S = requests.Session()
        URL = "https://fa.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "query",
            "format": "json",
            "titles": page_title,
            "prop": "pageimages",
            "piprop": "original"
        }
        res = S.get(url=URL, params=PARAMS)
        data = res.json()
        pages = data['query']['pages']
        for k, v in pages.items():
            return v.get('original', {}).get('source')
    except Exception:
        return None

def run_global_seeder():
    wiki_fa = wikipediaapi.Wikipedia(
        user_agent='WikiIranSeeder/2.0 (contact: your@email.com)',
        language='fa'
    )

    # لیست استان‌های ایران برای چرخه اصلی
    provinces = [
        "آذربایجان شرقی", "آذربایجان غربی", "اردبیل", "اصفهان", "البرز", "ایلام", "بوشهر", 
        "تهران", "چهارمحال و بختیاری", "خراسان جنوبی", "خراسان رضوی", "خراسان شمالی", 
        "خوزستان", "زنجان", "سمنان", "سیستان و بلوچستان", "فارس", "قزوین", "قم", 
        "کردستان", "کرمان", "کرمانشاه", "کهگیلویه و بویراحمد", "گلستان", "گیلان", 
        "لرستان", "مازندران", "مرکزی", "هرمزگان", "همدان", "یزد"
    ]

    print(f"🚀 شروع استخراج داده برای {len(provinces)} استان...")

    for province in provinces:
        print(f"\n📍 در حال پردازش استان: {province}")
        
        # تعریف ساختار دسته‌بندی برای هر استان
        categories_map = {
            f"استان {province}": {"title": f"استان {province}", "parent": None},
            f"شهرهای استان {province}": {"title": "شهرها", "parent": f"استان {province}"},
            f"روستاهای استان {province}": {"title": "روستاها", "parent": f"استان {province}"},
            f"جاذبه‌های گردشگری استان {province}": {"title": "گردشگری", "parent": f"استان {province}"},
            f"آثار تاریخی استان {province}": {"title": "آثار تاریخی", "parent": f"استان {province}"},
        }

        for wiki_cat_name, info in categories_map.items():
            # مدیریت دسته‌بندی در دیتابیس
            parent_obj = None
            if info['parent']:
                parent_obj = WikiCategory.objects.using('team6').filter(
                    slug=slugify(info['parent'], allow_unicode=True)
                ).first()

            db_cat, _ = WikiCategory.objects.using('team6').get_or_create(
                slug=slugify(wiki_cat_name, allow_unicode=True),
                defaults={'title_fa': info['title'], 'parent': parent_obj}
            )

            # خواندن صفحه دسته‌بندی از ویکی‌پدیا
            cat_page = wiki_fa.page(f"Category:{wiki_cat_name}")
            if not cat_page.exists():
                continue

            # محدود کردن تعداد مقالات برای هر دسته (مثلاً ۵ مورد برای سرعت بیشتر)
            members = [p for p in cat_page.categorymembers.values() if p.ns == wikipediaapi.Namespace.MAIN][:5]

            for page in members:
                try:
                    # ۱. گرفتن عکس
                    image_url = get_wiki_image(page.title)

                    # ۲. گرفتن عنوان انگلیسی از langlinks
                    en_title = page.langlinks['en'].title if 'en' in page.langlinks else None

                    # ۳. ساخت یا آپدیت مقاله
                    article, created = WikiArticle.objects.using('team6').update_or_create(
                        url=page.fullurl,
                        defaults={
                            'place_name': page.title,
                            'slug': slugify(page.title, allow_unicode=True)[:50] + "-" + str(now().microsecond)[:3],
                            'title_fa': page.title,
                            'title_en': en_title,
                            'body_fa': page.text,
                            'summary': page.summary[:1000],
                            'category': db_cat,
                            'featured_image_url': image_url,
                            'status': 'published',
                            'published_at': now(),
                            'view_count': 0
                        }
                    )

                    # ۴. ترجمه خودکار در صورت نبود داده
                    updated_fields = []
                    if not article.title_en:
                        article.title_en = GoogleTranslator(source='fa', target='en').translate(article.title_fa)
                        updated_fields.append('title_en')
                    
                    if not article.body_en:
                        # ترجمه فقط بخشی از متن برای جلوگیری از محدودیت گوگل
                        article.body_en = GoogleTranslator(source='fa', target='en').translate(article.body_fa[:2000])
                        updated_fields.append('body_en')

                    if updated_fields:
                        article.save(using='team6', update_fields=updated_fields)

                    # ۵. ثبت Revision
                    WikiArticleRevision.objects.using('team6').get_or_create(
                        article=article,
                        revision_no=1,
                        defaults={'body_fa': page.text, 'change_note': 'Global Import'}
                    )

                    print(f"  ✅ {page.title} ذخیره شد.")

                except Exception as e:
                    print(f"  ❌ خطا در {page.title}: {e}")

    print("\n🎉 عملیات با موفقیت به پایان رسید.")

if __name__ == "__main__":
    run_global_seeder()