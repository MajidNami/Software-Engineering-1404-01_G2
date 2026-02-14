from django import template

register = template.Library()


@register.filter(name="fa_enum")
def fa_enum(value):
    if value is None:
        return ""

    s = str(value).strip()
    sl = s.lower()

    mapping = {
        "economy": "اقتصادی",
        "economic": "اقتصادی",
        "economical": "اقتصادی",
        "medium": "متوسط",
        "normal": "متوسط",
        "standard": "متوسط",
        "moderate": "متوسط",
        "luxury": "لوکس",
        "lux": "لوکس",
        "draft": "پیش‌نویس",
        "active": "فعال",
        "finished": "تمام‌شده",
        "done": "تمام‌شده",
        "completed": "تمام‌شده",
        "cancelled": "لغوشده",
        "canceled": "لغوشده",
    }
    return mapping.get(sl, s)
