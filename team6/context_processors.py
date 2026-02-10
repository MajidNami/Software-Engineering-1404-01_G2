# team6/context_processors.py
from team6.models import ArticleNotification  # اصلاح نام مدل

def notifications_processor(request):
    """
    اعلان‌های کاربر را به تمپلیت اضافه می‌کند.
    - فقط اگر کاربر لاگین باشد
    - بدون نیاز به تغییر settings.py
    """
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"user_notifications": []}

    # گرفتن اعلان‌های فعال و خوانده نشده کاربر
    notifications = ArticleNotification.objects.filter(
        user_id=user.id,  # UUID
        is_active=True,
        is_read=False
    ).order_by("-created_at")[:10]  # ۱۰ اعلان آخر
    
    # تعداد اعلان‌های خوانده نشده
    unread_count = ArticleNotification.objects.filter(
        user_id=user.id,
        is_active=True,
        is_read=False
    ).count()
    
    return {
        "user_notifications": notifications,
        "unread_notifications_count": unread_count
    }