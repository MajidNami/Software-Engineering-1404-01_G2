# signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import WikiArticle, WikiTag, ArticleFollow, ArticleNotification
import threading
import time
from .services.llm_service import FreeAIService
from django.utils.text import slugify
import uuid
from django.db import transaction

# کش برای ذخیره old values
_article_old_cache = {}

def generate_ai_content(article):
    """تولید خلاصه و تگ در پس‌زمینه"""
    try:
        from .services.llm_service import FreeAIService
        llm_service = FreeAIService()
        
        summary = llm_service.generate_summary(article.body_fa)
        tags_list = llm_service.extract_tags(article.body_fa, article.title_fa)
        
        article.summary = summary
        article.save(update_fields=['summary'])
        
        for tag_name in tags_list:
            tag, created = WikiTag.objects.get_or_create(
                title_fa=tag_name,
                defaults={
                    'slug': tag_name.replace(' ', '-').replace('‌', '-')[:50],
                    'title_en': tag_name
                }
            )
            article.tags.add(tag)
            
    except Exception as e:
        print(f"⚠️ خطا در تولید AI: {e}")

@receiver(pre_save, sender=WikiArticle)
def capture_real_old_state(sender, instance, **kwargs):
    """ذخیره وضعیت REAL قدیمی مقاله از دیتابیس"""
    if instance.pk:  # فقط برای مقالات موجود
        try:
            # **خواندن از دیتابیس** نه از instance
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT body_fa, title_fa, category_id, featured_image_url 
                    FROM wiki_articles 
                    WHERE id_article = %s
                    """,
                    [str(instance.pk)]
                )
                row = cursor.fetchone()
                
                if row:
                    _article_old_cache[instance.pk] = {
                        'body_fa': row[0] or '',
                        'title_fa': row[1] or '',
                        'category_id': row[2],
                        'featured_image_url': row[3],
                        'timestamp': time.time()
                    }
        except Exception as e:
            print(f"⚠️ خطا در ذخیره وضعیت قدیمی REAL: {e}")

@receiver(post_save, sender=WikiArticle)
def simple_notify_article_change(sender, instance, created, **kwargs):
    """اعلان دقیق برای تغییرات مقاله"""
    if created:
        return
    
    # دریافت وضعیت قدیمی REAL
    old_state = None
    if instance.pk in _article_old_cache:
        old_state = _article_old_cache.pop(instance.pk)
    
    if not old_state:
        return
    
    # بررسی تغییرات با دقت
    body_changed = old_state['body_fa'] != instance.body_fa
    title_changed = old_state['title_fa'] != instance.title_fa
    category_changed = old_state['category_id'] != instance.category_id
    image_changed = old_state['featured_image_url'] != instance.featured_image_url
    
    # اگر هیچ تغییر مهمی نبود، خروج
    if not (body_changed or title_changed or category_changed or image_changed):
        return
    
    # **ایجاد پیام دقیق بر اساس نوع تغییر**
    changes_list = []
    
    if body_changed:
        changes_list.append("متن")
    
    if title_changed:
        changes_list.append("عنوان")
    
    if category_changed:
        # گرفتن نام دسته‌بندی‌ها
        try:
            from .models import WikiCategory
            old_category = WikiCategory.objects.get(id_category=old_state['category_id'])
            new_category = instance.category
            changes_list.append(f"دسته‌بندی ({old_category.title_fa} → {new_category.title_fa})")
        except:
            changes_list.append("دسته‌بندی")
    
    if image_changed:
        changes_list.append("تصویر شاخص")
    
    # ساخت پیام
    if len(changes_list) == 1:
        change_text = changes_list[0]
        message = f"{change_text} مقاله '{instance.title_fa}' ویرایش شد."
    else:
        changes_text = "، ".join(changes_list)
        message = f"مقاله '{instance.title_fa}' در بخش‌های {changes_text} ویرایش شد."
    
    # پیدا کردن دنبال‌کنندگان
    try:
        followers = ArticleFollow.objects.filter(
            article=instance, 
            notify=True
        )
        
        if not followers.exists():
            return
        
        # ایجاد اعلان برای همه دنبال‌کنندگان
        notification_count = 0
        
        # **تعیین نوع اعلان بر اساس مهم‌ترین تغییر**
        if body_changed:
            notification_type = 'edit'  # ویرایش متن
        elif title_changed:
            notification_type = 'edit'  # ویرایش عنوان
        elif category_changed:
            notification_type = 'category'  # تغییر دسته‌بندی
        elif image_changed:
            notification_type = 'image'  # تغییر تصویر
        else:
            notification_type = 'edit'
        
        for follow in followers:
            ArticleNotification.objects.create(
                user_id=follow.user_id,
                article=instance,
                notification_type=notification_type,
                message=message
            )
            notification_count += 1
        
    except Exception as e:
        import traceback
        traceback.print_exc()