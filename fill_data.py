import os
import django
import uuid
import re
from django.utils.text import slugify
from django.utils.timezone import now

# ۱. تنظیمات اولیه جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app404.settings')
django.setup()

import wikipediaapi
from team6.models import (
    WikiArticle, WikiCategory, WikiTag, 
    WikiArticleLink, WikiArticleRef, WikiArticleRevision
)

def run_advanced_seeder():
    wiki_fa = wikipediaapi.Wikipedia(
        user_agent='IsfahanFullProject/1.0 (contact: your@email.com)',
        language='fa'
    )

    # ۲. ساختار سلسله‌مراتبی اصفهان
    isfahan_categories = {
        "استان اصفهان": {"title": "استان اصفهان", "parent": None},
        "شهرهای استان اصفهان": {"title": "شهرها و بخش‌ها", "parent": "استان اصفهان"},
        "روستاهای استان اصفهان": {"title": "روستاها", "parent": "استان اصفهان"},
        "آثار تاریخی استان اصفهان": {"title": "آثار تاریخی و ملی", "parent": "استان اصفهان"},
        "جاذبه‌های گردشگری اصفهان": {"title": "گردشگری و طبیعت", "parent": "استان اصفهان"},
        "عمارت‌های تاریخی استان اصفهان": {"title": "بناها و عمارت‌ها", "parent": "آثار تاریخی استان اصفهان"},
        "باغ‌های استان اصفهان": {"title": "باغ‌ها و تفرجگاه‌ها", "parent": "جاذبه‌های گردشگری اصفهان"},
    }

    print("🚀 شروع فرآیند جامع استخراج داده...")

    # ذخیره موقت آیدی مقالات برای ایجاد لینک‌های داخلی در گام دوم
    processed_articles = {} 

    for wiki_cat_name, info in isfahan_categories.items():
        # ۳. مدیریت دسته‌بندی‌ها
        parent_obj = None
        if info['parent']:
            parent_obj = WikiCategory.objects.using('team6').filter(slug=slugify(info['parent'], allow_unicode=True)).first()

        db_cat, _ = WikiCategory.objects.using('team6').get_or_create(
            slug=slugify(wiki_cat_name, allow_unicode=True),
            defaults={'title_fa': info['title'], 'parent': parent_obj}
        )

        cat_page = wiki_fa.page(f"Category:{wiki_cat_name}")
        if not cat_page.exists(): continue

        # استخراج مقالات (محدود به ۱۵ مورد برای هر رده جهت تست اولیه)
        members = [p for p in cat_page.categorymembers.values() if p.ns == wikipediaapi.Namespace.MAIN][:15]

        for page in members:
            try:
                # ۴. استخراج اطلاعات انگلیسی (اگر باشد)
                en_title = page.langlinks['en'].title if 'en' in page.langlinks else None
                
                # ۵. ایجاد یا بروزرسانی مقاله اصلی
                article, created = WikiArticle.objects.using('team6').update_or_create(
                    url=page.fullurl,
                    defaults={
                        'place_name': page.title,
                        'slug': slugify(page.title, allow_unicode=True)[:50],
                        'title_fa': page.title,
                        'title_en': en_title,
                        'body_fa': page.text,
                        'summary': page.summary[:1000],
                        'category': db_cat,
                        'status': 'published',
                        'published_at': now(),
                        'view_count': 0
                    }
                )
                processed_articles[page.title] = article

                # ۶. پر کردن جدول Revision (تاریخچه نسخه اول)
                WikiArticleRevision.objects.using('team6').get_or_create(
                    article=article,
                    revision_no=1,
                    defaults={
                        'body_fa': page.text,
                        'change_note': 'Initial import from Wikipedia'
                    }
                )
