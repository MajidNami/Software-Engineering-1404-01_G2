import requests
from rest_framework.permissions import BasePermission
from django.conf import settings


class IsAuthenticatedViaCookie(BasePermission):
    """Verify auth via Core service, populate request.user_data"""
    def has_permission(self, request, view):
        if request.method == "OPTIONS":
            return True

        token = request.COOKIES.get("access_token")
        if not token:
            return False

        try:
            resp = requests.get(
                f"{settings.CORE_BASE_URL}/api/auth/verify/",
                cookies={"access_token": token},
                timeout=2
            )
            if resp.status_code == 200:
                request.user_data = {
                    "id": resp.headers.get("X-User-Id"),
                    "email": resp.headers.get("X-User-Email"),
                    "first_name": resp.headers.get("X-User-First-Name", ""),
                    "last_name": resp.headers.get("X-User-Last-Name", ""),
                }
                return True
        except Exception:
            pass
        return False


class IsOwnerOrReadOnly(BasePermission):
    """Allow read to all, write to owner only"""
    def has_object_permission(self, request, view, obj):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return hasattr(obj, "user_id") and str(obj.user_id) == request.user_data.get("id")
