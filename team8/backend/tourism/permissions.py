import jwt
from django.conf import settings
from rest_framework.permissions import BasePermission
from .models import User


def _get_user_from_token(request):
    """Extract and validate JWT from cookie or Authorization header. Attach user to request."""
    if hasattr(request, '_jwt_user'):
        return request._jwt_user

    token = request.COOKIES.get('access_token')
    if not token:
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        if auth.startswith('Bearer '):
            token = auth[7:]

    if not token:
        request._jwt_user = None
        return None

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        request._jwt_user = None
        return None

    try:
        user = User.objects.get(user_id=payload['user_id'])
    except User.DoesNotExist:
        request._jwt_user = None
        return None

    request._jwt_user = user
    request.user = user
    return user


class IsAuthenticated(BasePermission):
    """Standalone JWT authentication via cookie or Bearer header."""

    def has_permission(self, request, view):
        return _get_user_from_token(request) is not None


class IsOwnerOrReadOnly(BasePermission):
    """Object-level: owners can write, everyone else read-only."""

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        user = _get_user_from_token(request)
        return user and obj.user_id == user.user_id


class AllowAny(BasePermission):
    """Allow any access. Optionally attaches user if token present."""

    def has_permission(self, request, view):
        _get_user_from_token(request)  # attach user if available, but don't block
        return True


class IsAdmin(BasePermission):
    """Only users with is_admin=True."""

    def has_permission(self, request, view):
        user = _get_user_from_token(request)
        return user is not None and user.is_admin
