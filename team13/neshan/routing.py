# مسیریابی نشان — با ترافیک، بدون ترافیک، عابر پیاده.
# با ترافیک: https://platform.neshan.org/docs/api/routing-category/routing/
# بدون ترافیک: https://platform.neshan.org/docs/api/routing-category/noTraffic-routing-api/
# عابر پیاده: https://platform.neshan.org/docs/api/routing-category/routing_pedestrian/

import logging
from .config import (
    get_api_key,
    is_configured,
    NESHAN_API_BASE,
    NESHAN_DIRECTION_PATH,
    NESHAN_DIRECTION_NO_TRAFFIC_PATH,
)

logger = logging.getLogger(__name__)

# نوع وسیله برای API نشان
VEHICLE_CAR = "car"
VEHICLE_MOTORCYCLE = "motorcycle"
VEHICLE_PEDESTRIAN = "pedestrian"


def _request_direction(url_path, params, api_key, timeout=15):
    """درخواست GET به یک endpoint مسیریابی نشان؛ خروجی (distance_km, duration_seconds, route_geometry)."""
    try:
        import requests
        url = f"{NESHAN_API_BASE.rstrip('/')}{url_path}"
        headers = {"Api-Key": api_key}
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            logger.debug("Neshan direction HTTP %s: %s", resp.status_code, resp.text[:200])
            return None, None, None
        data = resp.json()
        routes = data.get("routes") or []
        if not routes:
            return None, None, None
        first = routes[0]
        legs = first.get("legs") or []
        distance_m = None
        duration_s = None
        for leg in legs:
            d = (leg.get("distance") or {}).get("value")
            t = (leg.get("duration") or {}).get("value")
            if d is not None:
                distance_m = (distance_m or 0) + d
            if t is not None:
                duration_s = (duration_s or 0) + t
        dist_km = (distance_m / 1000.0) if distance_m is not None else None
        return dist_km, duration_s, first
    except Exception as e:
        logger.debug("Neshan direction failed: %s", e)
        return None, None, None


def _build_direction_params(lat_origin, lng_origin, lat_dest, lng_dest, vehicle_type,
                            waypoints=None, avoid_traffic_zone=False, avoid_odd_even_zone=False,
                            alternative=False, bearing=None):
    """ساخت params مشترک برای direction (با ترافیک و بدون ترافیک)."""
    params = {
        "type": vehicle_type,
        "origin": f"{lat_origin},{lng_origin}",
        "destination": f"{lat_dest},{lng_dest}",
    }
    if waypoints:
        if isinstance(waypoints, (list, tuple)):
            parts = []
            for wp in waypoints:
                if isinstance(wp, (list, tuple)) and len(wp) >= 2:
                    parts.append(f"{wp[0]},{wp[1]}")
                elif hasattr(wp, "lat") and hasattr(wp, "lng"):
                    parts.append(f"{wp.lat},{wp.lng}")
            if parts:
                params["waypoints"] = "|".join(parts)
        else:
            params["waypoints"] = str(waypoints)
    if avoid_traffic_zone:
        params["avoidTrafficZone"] = "true"
    if avoid_odd_even_zone:
        params["avoidOddEvenZone"] = "true"
    if alternative:
        params["alternative"] = "true"
    if bearing is not None and 0 <= bearing <= 360:
        params["bearing"] = int(bearing)
    return params


def fetch_route_eta(lng_origin, lat_origin, lng_dest, lat_dest, vehicle_type=VEHICLE_CAR,
                    waypoints=None, avoid_traffic_zone=False, avoid_odd_even_zone=False, alternative=False, bearing=None):
    """
    فاصله (کیلومتر)، زمان (ثانیه) و geometry مسیر از سرویس مسیریابی با ترافیک نشان.
    خروجی: (distance_km, duration_seconds, route_geometry). نوع وسیله: car | motorcycle.
    """
    if not is_configured():
        return None, None, None
    api_key = get_api_key()
    if vehicle_type not in (VEHICLE_CAR, VEHICLE_MOTORCYCLE):
        vehicle_type = VEHICLE_CAR
    params = _build_direction_params(
        lat_origin, lng_origin, lat_dest, lng_dest, vehicle_type,
        waypoints=waypoints, avoid_traffic_zone=avoid_traffic_zone,
        avoid_odd_even_zone=avoid_odd_even_zone, alternative=alternative, bearing=bearing,
    )
    return _request_direction(NESHAN_DIRECTION_PATH, params, api_key)


def fetch_route_eta_no_traffic(lng_origin, lat_origin, lng_dest, lat_dest,
                               waypoints=None, avoid_traffic_zone=False, avoid_odd_even_zone=False,
                               alternative=False, bearing=None):
    """
    مسیریابی بدون ترافیک (No Traffic Routing API) — فقط خودرو.
    مستندات: https://platform.neshan.org/docs/api/routing-category/noTraffic-routing-api/
    Endpoint: GET https://api.neshan.org/v4/direction/no-traffic
    خروجی: (distance_km, duration_seconds, route_geometry).
    """
    if not is_configured():
        return None, None, None
    api_key = get_api_key()
    params = _build_direction_params(
        lat_origin, lng_origin, lat_dest, lng_dest, VEHICLE_CAR,
        waypoints=waypoints, avoid_traffic_zone=avoid_traffic_zone,
        avoid_odd_even_zone=avoid_odd_even_zone, alternative=alternative, bearing=bearing,
    )
    return _request_direction(NESHAN_DIRECTION_NO_TRAFFIC_PATH, params, api_key)


def fetch_route_eta_pedestrian(lng_origin, lat_origin, lng_dest, lat_dest,
                               waypoints=None, alternative=False, bearing=None):
    """
    مسیریابی عابر پیاده (Pedestrian Routing API) — همان endpoint با type=pedestrian.
    مستندات: https://platform.neshan.org/docs/api/routing-category/routing_pedestrian/
    Endpoint: GET https://api.neshan.org/v4/direction
    پارامترها: type=pedestrian، origin، destination؛ اختیاری: waypoints، alternative، bearing.
    خروجی: (distance_km, duration_seconds, route_geometry).
    """
    if not is_configured():
        return None, None, None
    api_key = get_api_key()
    params = _build_direction_params(
        lat_origin, lng_origin, lat_dest, lng_dest, VEHICLE_PEDESTRIAN,
        waypoints=waypoints, avoid_traffic_zone=False, avoid_odd_even_zone=False,
        alternative=alternative, bearing=bearing,
    )
    return _request_direction(NESHAN_DIRECTION_PATH, params, api_key)
