# Context processor برای قرار دادن وضعیت کاربر (Core) و کلید نقشهٔ نشان در قالب‌های team13

from .core_auth import get_current_user_info
from .neshan.config import get_web_key


def team13_user_context(request):
    """
    فقط برای درخواست‌های زیرمسیر /team13/ متغیر team13_user و NESHAN_MAP_KEY را به context اضافه می‌کند.
    NESHAN_MAP_KEY (کلید وب نشان) از neshan.config.get_web_key برای لود SDK نقشه در فرانت استفاده می‌شود.
    """
    if not request.path.startswith("/team13/"):
        return {}
    user_info = get_current_user_info(request)
    ctx = {"team13_user": user_info}
    try:
        ctx["NESHAN_MAP_KEY"] = get_web_key() or ""
    except Exception:
        ctx["NESHAN_MAP_KEY"] = ""
    return ctx
