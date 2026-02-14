# تبدیل مختصات جغرافیایی به آدرس متنی برای ذخیره در دیتابیس
# در صورت تنظیم NESHAN_API_KEY از سرویس نشان استفاده می‌شود؛ وگرنه فرمت عرض/طول.


def address_from_coords(latitude, longitude):
    """
    بر اساس عرض و طول جغرافیایی یک رشتهٔ آدرس معتبر برای ذخیره در دیتابیس برمی‌گرداند.
    اگر کلید نشان تنظیم شده باشد از API تبدیل نقطه به آدرس نشان استفاده می‌کند؛ وگرنه از فرمت عرض/طول.
    """
    try:
        lat = float(latitude)
        lng = float(longitude)
    except (TypeError, ValueError):
        return "عرض و طول نامعتبر"
    try:
        from .neshan import reverse_geocode_address
        addr = reverse_geocode_address(lat, lng)
        if addr and isinstance(addr, str) and addr.strip():
            return addr.strip()
    except Exception:
        pass
    return "عرض جغرافیایی: {:.6f}، طول جغرافیایی: {:.6f}".format(lat, lng)
