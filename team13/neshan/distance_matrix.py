# ماتریس فاصله (Distance Matrix) نشان — فاصله و زمان بین چند مبدأ و چند مقصد.
# مستندات: https://platform.neshan.org/docs/api/routing-category/distance-matrix/
# با ترافیک: GET https://api.neshan.org/v1/distance-matrix
# بدون ترافیک: GET https://api.neshan.org/v1/distance-matrix/no-traffic

import logging
from .config import (
    get_api_key,
    is_configured,
    NESHAN_API_BASE,
    NESHAN_DISTANCE_MATRIX_PATH,
    NESHAN_DISTANCE_MATRIX_NO_TRAFFIC_PATH,
)

logger = logging.getLogger(__name__)

TYPE_CAR = "car"
TYPE_MOTORCYCLE = "motorcycle"


def _points_to_string(points):
    """تبدیل لیست نقاط به رشتهٔ lat,lng|lat,lng|..."""
    parts = []
    for p in points:
        if isinstance(p, str) and "," in p:
            parts.append(p.strip())
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            parts.append(f"{p[0]},{p[1]}")
        elif hasattr(p, "lat") and hasattr(p, "lng"):
            parts.append(f"{p.lat},{p.lng}")
        elif isinstance(p, dict):
            lat = p.get("lat") or p.get("latitude")
            lng = p.get("lng") or p.get("longitude")
            if lat is not None and lng is not None:
                parts.append(f"{lat},{lng}")
    return "|".join(parts) if parts else ""


def fetch_distance_matrix(origins, destinations, vehicle_type=TYPE_CAR, no_traffic=False):
    """
    ماتریس فاصله و زمان بین نقاط مبدأ و مقصد.
    origins: لیست نقاط مبدأ (هر نقطه lat,lng یا [lat,lng] یا شیء با .lat/.lng).
    destinations: لیست نقاط مقصد (همان فرمت).
    vehicle_type: car | motorcycle.
    no_traffic: True = بدون ترافیک، False = با ترافیک لحظه‌ای.
    خروجی: پاسخ کامل API شامل status، rows، origin_addresses، destination_addresses؛ در صورت خطا None.
    rows[i].elements[j] = فاصله/زمان از origin i به destination j.
    """
    if not is_configured():
        return None
    api_key = get_api_key()
    if vehicle_type not in (TYPE_CAR, TYPE_MOTORCYCLE):
        vehicle_type = TYPE_CAR
    origins_str = _points_to_string(origins) if not isinstance(origins, str) else origins
    destinations_str = _points_to_string(destinations) if not isinstance(destinations, str) else destinations
    if not origins_str or not destinations_str:
        return None
    try:
        import requests
        path = NESHAN_DISTANCE_MATRIX_NO_TRAFFIC_PATH if no_traffic else NESHAN_DISTANCE_MATRIX_PATH
        url = f"{NESHAN_API_BASE.rstrip('/')}{path}"
        params = {
            "type": vehicle_type,
            "origins": origins_str,
            "destinations": destinations_str,
        }
        headers = {"Api-Key": api_key}
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        if resp.status_code != 200:
            logger.debug("Neshan distance-matrix HTTP %s: %s", resp.status_code, resp.text[:200])
            return None
        data = resp.json()
        if data.get("status") != "Ok":
            return None
        return data
    except Exception as e:
        logger.debug("Neshan distance-matrix failed: %s", e)
        return None
