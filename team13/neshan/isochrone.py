# محدوده در دسترس (Isochrone) نشان — محدوده قابل دسترسی بر اساس زمان یا مسافت.
# مستندات: https://platform.neshan.org/docs/api/routing-category/isochrone/
# Endpoint: GET https://api.neshan.org/v1/isochrone

import logging
from .config import get_api_key, is_configured, NESHAN_API_BASE, NESHAN_ISOCHRONE_PATH

logger = logging.getLogger(__name__)


def fetch_isochrone(lat, lng, distance_km=None, time_minutes=None, polygon=False, denoise=0):
    """
    محدوده‌ای که از نقطه مرکز در زمان یا مسافت معین قابل دسترسی است.
    lat, lng: مختصات مرکز.
    distance_km: حداکثر مسافت قابل دسترسی (کیلومتر) — حداقل یکی از distance_km یا time_minutes اجباری است.
    time_minutes: حداکثر زمان قابل دسترسی (دقیقه).
    polygon: True = خروجی Polygon، False = LineString (پیش‌فرض).
    denoise: 0 تا 1؛ هرچه به 1 نزدیک‌تر، پولیگان ساده‌تر (پیش‌فرض 0).
    خروجی: GeoJSON FeatureCollection یا None در صورت خطا.
    """
    if not is_configured():
        return None
    if distance_km is None and time_minutes is None:
        return None
    if lat is None or lng is None:
        return None
    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError):
        return None
    api_key = get_api_key()
    params = {
        "location": f"{lat_f},{lng_f}",
    }
    if distance_km is not None:
        try:
            params["distance"] = float(distance_km)
        except (TypeError, ValueError):
            pass
    if time_minutes is not None:
        try:
            params["time"] = float(time_minutes)
        except (TypeError, ValueError):
            pass
    if not params.get("distance") and not params.get("time"):
        return None
    params["polygon"] = "true" if polygon else "false"
    if denoise is not None and 0 <= denoise <= 1:
        params["denoise"] = denoise
    try:
        import requests
        url = f"{NESHAN_API_BASE.rstrip('/')}{NESHAN_ISOCHRONE_PATH}"
        headers = {"Api-Key": api_key}
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        if resp.status_code != 200:
            logger.debug("Neshan isochrone HTTP %s: %s", resp.status_code, resp.text[:200])
            return None
        return resp.json()
    except Exception as e:
        logger.debug("Neshan isochrone failed: %s", e)
        return None
