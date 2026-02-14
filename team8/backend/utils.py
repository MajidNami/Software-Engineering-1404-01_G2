import requests
from rest_framework.views import exception_handler
from django.conf import settings


def custom_exception_handler(exc, context):
    """Clean error responses"""
    response = exception_handler(exc, context)
    if response:
        response.data = {"error": response.data}
    return response


def call_ai_service(endpoint, data, timeout=10):
    """Call AI service endpoint"""
    try:
        resp = requests.post(
            f"{settings.AI_SERVICE_URL}/{endpoint}",
            json=data,
            timeout=timeout
        )
        return resp.json() if resp.status_code == 200 else None
    except Exception:
        return None
        metadata: Additional metadata dict
    """
    try:
        ActivityLog.objects.create(
            user=user,
            action_type=action_type,
            target_id=target_id,
            metadata=metadata or {}
        )
    except Exception as e:
        print(f"Failed to log activity: {e}")


def verify_user_with_core(cookies):
    """
    Verify user authentication with Core service
    
    Args:
        cookies: Request cookies containing access_token
    
    Returns:
        dict: User info or None if not authenticated
    """
    try:
        from .settings import CORE_BASE_URL
        
        response = requests.get(
            f"{CORE_BASE_URL}/api/auth/verify/",
            cookies=cookies,
            timeout=3
        )
        
        if response.status_code == 200:
            return {
                'id': response.headers.get('X-User-Id'),
                'email': response.headers.get('X-User-Email'),
                'first_name': response.headers.get('X-User-First-Name', ''),
                'last_name': response.headers.get('X-User-Last-Name', ''),
                'age': response.headers.get('X-User-Age', ''),
            }
        return None
    
    except requests.exceptions.RequestException:
        return None


def create_notification(user, title, message):
    """
    Create notification for user
    
    Args:
        user: User instance
        title: Notification title
        message: Notification message
    """
    from .models import Notification
    
    try:
        Notification.objects.create(
            user=user,
            title=title,
            message=message
        )
    except Exception as e:
        print(f"Failed to create notification: {e}")
