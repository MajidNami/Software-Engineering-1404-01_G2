import logging
from rest_framework.views import exception_handler
from django.conf import settings

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {"error": response.data}
    return response


def log_activity(user, action_type, target_id=None, metadata=None):
    from .models import ActivityLog
    try:
        ActivityLog.objects.create(
            user=user,
            action_type=action_type,
            target_id=str(target_id) if target_id else None,
            metadata=metadata or {},
        )
    except Exception:
        logger.exception("Failed to log activity %s", action_type)


def create_notification(user, title, message):
    from .models import Notification
    try:
        Notification.objects.create(user=user, title=title, message=message)
    except Exception:
        logger.exception("Failed to create notification for user %s", user.user_id)


def notify_post_owner(post, action_user, event):
    """Notify the post owner about an action (reply, vote, report)."""
    if post.user_id == action_user.user_id:
        return
    titles = {
        'reply': 'New reply',
        'like': 'Your post was liked',
        'dislike': 'Your post was disliked',
        'report': 'Your post was reported',
    }
    messages = {
        'reply': f'{action_user.username} replied to your post.',
        'like': f'{action_user.username} liked your post.',
        'dislike': f'{action_user.username} disliked your post.',
        'report': 'Your post has been reported for review.',
    }
    create_notification(post.user, titles.get(event, event), messages.get(event, event))


def validate_upload(file):
    """Validate file size and type. Returns error string or None."""
    if file.size > settings.MAX_UPLOAD_SIZE:
        return f"File too large. Max {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB."
    allowed = settings.ALLOWED_IMAGE_TYPES + settings.ALLOWED_VIDEO_TYPES
    if file.content_type not in allowed:
        return f"Unsupported type {file.content_type}."
    return None
