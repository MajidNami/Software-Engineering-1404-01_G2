# team6/templatetags/notification_tags.py
from django import template
from team6.models import ArticleFollow

register = template.Library()

@register.filter
def is_user_following(article, user):
    """بررسی آیا کاربر مقاله را دنبال کرده است"""
    if not user.is_authenticated:
        return False
    return ArticleFollow.objects.filter(
        user_id=user.id,
        article=article
    ).exists()

@register.filter
def get_notification_icon(notification_type):
    """آیکون مناسب برای نوع اعلان"""
    icons = {
        'edit': 'fa-edit',
        'image': 'fa-image',
        'tags': 'fa-tags',
        'category': 'fa-folder',
        'new': 'fa-plus'
    }
    return icons.get(notification_type, 'fa-bell')

@register.filter
def get_notify_status(article, user):
    if not user.is_authenticated:
        return False

    return ArticleFollow.objects.filter(
        user_id=user.id,
        article=article,
        notify=True
    ).exists()
