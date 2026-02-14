# نگاشت نقطه بر نقشه (Map Matching) نشان — نگاشت نقاط خام (مثلاً GPS) به مسیر واقعی روی نقشه.
# مستندات: https://platform.neshan.org/docs/api/routing-category/map-matching/
# Endpoint: POST https://api.neshan.org/v3/map-matching
# Body: JSON { "path": "lat1,lng1|lat2,lng2|..." } — حداقل ۲، حداکثر ۱۰۰۰ نقطه.

import logging
from .config import get_api_key, is_configured, NESHAN_API_BASE, NESHAN_MAP_MATCHING_PATH

logger = logging.getLogger(__name__)


def fetch_map_matching(path):
    """
    نگاشت مجموعه نقاط به محتمل‌ترین مسیر روی نقشه.
    path: رشتهٔ lat,lng|lat,lng|... یا لیست نقاط ([lat,lng], ...) یا شیء با .lat/.lng.
    خروجی: { "snappedPoints": [...], "geometry": "encoded_polyline" } یا None.
    snappedPoint: { "location": [lat, lng], "originalIndex": int }.
    """
    if not is_configured():
        return None
    if not path:
        return None
    if isinstance(path, str):
        path_str = path.strip()
        parts = [p.strip() for p in path_str.split("|") if p.strip()]
    else:
        parts = []
        for p in path:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                parts.append(f"{p[0]},{p[1]}")
            elif hasattr(p, "lat") and hasattr(p, "lng"):
                parts.append(f"{p.lat},{p.lng}")
            elif isinstance(p, dict):
                lat = p.get("lat") or p.get("latitude")
                lng = p.get("lng") or p.get("longitude")
                if lat is not None and lng is not None:
                    parts.append(f"{lat},{lng}")
        path_str = "|".join(parts)
    if len(parts) < 2:
        return None
    if len(parts) > 1000:
        logger.debug("Neshan map-matching: more than 1000 points, truncating")
        path_str = "|".join(parts[:1000])
    api_key = get_api_key()
    try:
        import requests
        url = f"{NESHAN_API_BASE.rstrip('/')}{NESHAN_MAP_MATCHING_PATH}"
        headers = {"Api-Key": api_key, "Content-Type": "application/json"}
        payload = {"path": path_str}
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 404:
            logger.debug("Neshan map-matching 404: no route found for path")
            return None
        if resp.status_code != 200:
            logger.debug("Neshan map-matching HTTP %s: %s", resp.status_code, resp.text[:200])
            return None
        return resp.json()
    except Exception as e:
        logger.debug("Neshan map-matching failed: %s", e)
        return None
