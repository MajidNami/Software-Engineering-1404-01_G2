# یکپارچه‌سازی با احراز هویت Core — مرحله ۶
# در صورت تنظیم CORE_BASE_URL، وضعیت کاربر از /api/auth/me گرفته می‌شود؛ وگرنه از request.user همین سرور.

import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_current_user_info(request):
    """
    وضعیت کاربر جاری را برمی‌گرداند تا در UI (ورود/خروج، نام کاربر) استفاده شود.

    - اگر CORE_BASE_URL تنظیم شده باشد: درخواست GET به CORE_BASE_URL/api/auth/me/
      با ارسال کوکی‌های درخواست فعلی؛ در صورت موفقیت خروجی user از JSON.
    - در غیر این صورت: از request.user (همان سرور) استفاده می‌شود.

    خروجی در صورت احراز هویت موفق: dict با کلیدهای email, first_name, last_name, age
    در غیر این صورت: None
    """
    base_url = getattr(settings, "CORE_BASE_URL", None) or ""
    if base_url:
        return _fetch_user_from_core(request, base_url.rstrip("/"))
    return _user_from_request(request)


def _user_from_request(request):
    """استفاده از request.user همین سرور (همان‌دمان با Core)."""
    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        return None
    return {
        "email": getattr(user, "email", "") or "",
        "first_name": getattr(user, "first_name", "") or "",
        "last_name": getattr(user, "last_name", "") or "",
        "age": getattr(user, "age", None),
    }


def _fetch_user_from_core(request, base_url):
    """فراخوانی Core برای دریافت وضعیت کاربر با ارسال کوکی."""
    try:
        import requests
    except ImportError:
        logger.warning("برای فراخوانی Core، پکیج requests لازم است.")
        return _user_from_request(request)

    url = f"{base_url}/api/auth/me/"
    cookies = dict(request.COOKIES) if request.COOKIES else {}
    headers = {"Accept": "application/json"}
    try:
        resp = requests.get(url, cookies=cookies, headers=headers, timeout=3)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data.get("ok") or "user" not in data:
            return None
        u = data["user"]
        return {
            "email": u.get("email") or "",
            "first_name": u.get("first_name") or "",
            "last_name": u.get("last_name") or "",
            "age": u.get("age"),
        }
    except Exception as e:
        logger.debug("Core auth request failed: %s", e)
        return None
