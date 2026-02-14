# جستجوی مکان‌مبنا (Search API) نشان — بر اساس نقطه مرجع و عبارت جستجو.
# مستندات: https://platform.neshan.org/docs/api/search-category/search/
# Endpoint: GET https://api.neshan.org/v1/search
# پارامترهای اجباری: term، lat، lng. حداکثر ۳۰ نتیجه در هر درخواست.

import logging
from .config import get_api_key, is_configured, NESHAN_API_BASE, NESHAN_SEARCH_PATH

logger = logging.getLogger(__name__)

# مرکز پیش‌فرض (تهران) وقتی lat/lng از فراخوان‌دهنده ارسال نشود
DEFAULT_LAT = 35.6892
DEFAULT_LNG = 51.3890


def _search_raw(term, lat_f, lng_f):
    """یک درخواست GET به API جستجو؛ خروجی خام { count, items } یا در خطا None. API حداکثر ۳۰ نتیجه برمی‌گرداند."""
    if not is_configured():
        return None
    api_key = get_api_key()
    try:
        import requests
        url = f"{NESHAN_API_BASE.rstrip('/')}{NESHAN_SEARCH_PATH}"
        params = {"term": term, "lat": lat_f, "lng": lng_f}
        headers = {"Api-Key": api_key}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            logger.debug("Neshan search HTTP %s: %s", resp.status_code, resp.text[:200])
            return None
        return resp.json()
    except Exception as e:
        logger.debug("Neshan search failed: %s", e)
        return None


def search_autocomplete(query, lat=None, lng=None, limit=10):
    """
    جستجوی مکان‌مبنا با API نشان؛ نتایج بر اساس فاصله از نقطه مرجع مرتب می‌شوند.
    query: عبارت جستجو (term).
    lat, lng: مختصات نقطه مرجع (برای API اجباری؛ در صورت ندادن از مرکز پیش‌فرض استفاده می‌شود).
    limit: حداکثر تعداد نتیجه (API حداکثر ۳۰ برمی‌گرداند).
    خروجی: لیست آیتم‌های { title, address, neighbourhood, region, type, category, lat, lng, location }.
    """
    data = search_response(query, lat=lat, lng=lng, limit=limit)
    return data.get("items") or []


def search_response(query, lat=None, lng=None, limit=30):
    """
    جستجوی مکان‌مبنا با یک درخواست؛ خروجی مطابق مستندات: { count, items }.
    items هر کدام: title, address, neighbourhood, region, type, category, location: { x: lng, y: lat }, lat, lng.
    """
    term = (query or "").strip()
    if not term:
        return {"count": 0, "items": []}
    lat_val = lat if lat is not None else DEFAULT_LAT
    lng_val = lng if lng is not None else DEFAULT_LNG
    try:
        lat_f = float(lat_val)
        lng_f = float(lng_val)
    except (TypeError, ValueError):
        lat_f, lng_f = DEFAULT_LAT, DEFAULT_LNG
    limit = min(30, max(1, int(limit)))
    data = _search_raw(term, lat_f, lng_f)
    if not data:
        return {"count": 0, "items": []}
    count = int(data.get("count", 0))
    items_raw = data.get("items") or []
    if not isinstance(items_raw, list):
        return {"count": count, "items": []}
    out = []
    for item in items_raw[:limit]:
        if not isinstance(item, dict):
            continue
        loc = item.get("location") or {}
        # مستندات: location.x = طول (longitude)، location.y = عرض (latitude)
        lng_out = loc.get("x")
        lat_out = loc.get("y")
        if lng_out is None and lat_out is None:
            lng_out = item.get("lng") or item.get("lon")
            lat_out = item.get("lat")
        if lat_out is None or lng_out is None:
            continue
        try:
            lat_out = float(lat_out)
            lng_out = float(lng_out)
        except (TypeError, ValueError):
            continue
        out.append({
            "title": item.get("title") or item.get("name") or "",
            "address": item.get("address") or "",
            "neighbourhood": item.get("neighbourhood") or "",
            "region": item.get("region") or "",
            "type": item.get("type") or "",
            "category": item.get("category") or "",
            "location": {"x": lng_out, "y": lat_out},
            "lat": lat_out,
            "lng": lng_out,
        })
    return {"count": count, "items": out}


def search_count(query, lat=None, lng=None):
    """
    فقط تعداد نتایج جستجو. از search_response استفاده می‌کند تا یک درخواست کافی باشد.
    """
    data = search_response(query, lat=lat, lng=lng, limit=1)
    return data.get("count", 0)
