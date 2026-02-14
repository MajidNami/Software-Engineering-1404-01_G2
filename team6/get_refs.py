from team6.models import WikiArticle, WikiArticleRef
import uuid

# تعریف بانک منابع بر اساس موضوع (Keyword-based)
reference_bank = {
    'محلات': [
        {"title": "چشمه‌های آبگرم محلات؛ خواص درمانی و گردشگری", "url": "https://www.isna.ir/news/98051507421/", "pub": "ایسنا"},
        {"title": "راهنمای سفر به قطب گل و گیاه ایران", "url": "https://www.visitiran.ir/fa/destination/mahallat", "pub": "ویزیت ایران"}
    ],
    'تاریخ': [
        {"title": "اسناد تاریخی و باستان‌شناسی ایران", "url": "https://irandoc.ac.ir", "pub": "پژوهشگاه ایران‌داک"},
        {"title": "جستجوی آثار ثبت شده در فهرست آثار ملی", "url": "https://mcth.ir/national-heritage", "pub": "میراث فرهنگی"}
    ],
    'طبیعت': [
        {"title": "نقشه مناطق حفاظت شده و پارک‌های ملی ایران", "url": "https://doe.ir", "pub": "محیط زیست"},
        {"title": "معرفی غارها و جاذبه‌های طبیعی ایران", "url": "https://irandeserts.com", "pub": "کویرها و بیابان‌ها"}
    ],
    'گردشگری': [
        {"title": "پایگاه جامع اطلاعات گردشگری ایران", "url": "https://www.itto.org", "pub": "ITTO"},
        {"title": "دانشنامه سفر و گردشگری ایران‌گرد", "url": "https://irangard.com", "pub": "ایران‌گرد"}
    ]
}

# منبع پیش‌فرض (اگر هیچ کلمه‌ای پیدا نشد)
default_ref = {"title": "پایگاه اطلاع‌رسانی خبرگزاری رسمی جمهوری اسلامی", "url": "https://www.irna.ir", "pub": "ایرنا"}

articles = WikiArticle.objects.all()
created_count = 0

for article in articles:
    title = article.title_fa
    assigned = False
    
    # بررسی کلمات کلیدی در عنوان مقاله
    for keyword, refs in reference_bank.items():
        if keyword in title:
            # اضافه کردن تمام رفرنس‌های مربوط به آن کلمه کلیدی
            for r in refs:
                WikiArticleRef.objects.get_or_create(
                    article=article,
                    url=r['url'],
                    defaults={
                        'title': r['title'],
                        'publisher': r['pub']
                    }
                )
            assigned = True
            break # برای هر مقاله یک گروه رفرنس کافی است
    
    # اگر کلمه‌ای پیدا نشد، منبع عمومی بده
    if not assigned:
        WikiArticleRef.objects.get_or_create(
            article=article,
            url=default_ref['url'],
            defaults={
                'title': default_ref['title'],
                'publisher': default_ref['pub']
            }
        )
    created_count += 1

print(f"✅ پردازش تمام شد. برای {created_count} مقاله رفرنس متناسب با موضوع ثبت شد.")