# تبدیل مختصات به آدرس (Reverse) و آدرس به مختصات (Geocoding) با API نشان
# Reverse: https://platform.neshan.org/docs/api/search-category/reverse-geocoding/
# Geocoding: https://platform.neshan.org/docs/api/search-category/geocoding/

import json
import logging
from urllib.parse import quote

from .config import (
    NESHAN_API_BASE,
    NESHAN_GEOCODING_PATH,
    NESHAN_GEOCODING_PLUS_PATH,
    NESHAN_REVERSE_PATH,
    get_api_key,
    is_configured,
)

logger = logging.getLogger(__name__)


def reverse_geocode(lat, lng):
    """
    تبدیل نقطه (عرض، طول) به آدرس با API نشان (v5/reverse).
    خروجی: دیکشنری کامل پاسخ شامل status، formatted_address، route_name، route_type،
    neighbourhood، city، state، place، municipality_zone، in_traffic_zone، in_odd_even_zone،
    village، county، district؛ در صورت خطا None.
    """
    if not is_configured():
        return None
    try:
        lat_f = float(lat)
        lng_f = float(lng)
    except (TypeError, ValueError):
        return None
    api_key = get_api_key()
    try:
        import requests
        url = f"{NESHAN_API_BASE.rstrip('/')}{NESHAN_REVERSE_PATH}"
        params = {"lat": lat_f, "lng": lng_f}
        headers = {"Api-Key": api_key}
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            logger.debug("Neshan reverse HTTP %s: %s", resp.status_code, resp.text[:200])
            return None
        data = resp.json()
        if not isinstance(data, dict):
            return None
        if data.get("status") != "OK":
            return None
        return data
    except Exception as e:
        logger.debug("Neshan reverse failed: %s", e)
        return None


def reverse_geocode_address(lat, lng):
    """
    فقط رشتهٔ آدرس کامل (formatted_address) برای نقطه؛ برای استفاده در geo_utils و جاهایی که فقط متن آدرس لازم است.
    """
    data = reverse_geocode(lat, lng)
    if not data:
        return None
    return data.get("formatted_address") or None


def geocode(
    address,
    province=None,
    city=None,
    location=None,
    extent=None,
    plus=False,
):
    """
    تبدیل آدرس متنی به مختصات (Geocoding) با API نشان.
    مستندات: https://platform.neshan.org/docs/api/search-category/geocoding/
    درخواست: GET با query param json (بدنهٔ JSON کدشده در URL).

    آرگومان‌ها:
        address (str): آدرس مورد نظر — اجباری.
        province (str): استان — اختیاری.
        city (str): شهر — اختیاری.
        location (dict): مرکز جستجو؛ کلیدها: latitude, longitude — اختیاری.
        extent (dict): ناحیه جستجو؛ کلیدها: southWest, northEast (هر کدام {latitude, longitude}) — اختیاری.
        plus (bool): True برای سرویس پلاس (کدپستی/پلاک در تهران، مشهد، کرج، اصفهان، اهواز).

    خروجی:
        دیکشنری با کلید items (لیست حداکثر ۵ نتیجه؛ هر آیتم: location, province, city, neighbourhood, unMatchedTerm)
        یا None در صورت خطا.
    """
    if not is_configured():
        return None
    address = (address or "").strip()
    if not address:
        return None
    payload = {"address": address}
    if province:
        payload["province"] = str(province).strip()
    if city:
        payload["city"] = str(city).strip()
    if location and isinstance(location, dict):
        lat = location.get("latitude")
        lng = location.get("longitude")
        if lat is not None and lng is not None:
            try:
                payload["location"] = {"latitude": float(lat), "longitude": float(lng)}
            except (TypeError, ValueError):
                pass
    if extent and isinstance(extent, dict):
        sw = extent.get("southWest")
        ne = extent.get("northEast")
        if isinstance(sw, dict) and isinstance(ne, dict):
            try:
                payload["extent"] = {
                    "southWest": {"latitude": float(sw.get("latitude")), "longitude": float(sw.get("longitude"))},
                    "northEast": {"latitude": float(ne.get("latitude")), "longitude": float(ne.get("longitude"))},
                }
            except (TypeError, ValueError, AttributeError):
                pass
    path = NESHAN_GEOCODING_PLUS_PATH if plus else NESHAN_GEOCODING_PATH
    base = NESHAN_API_BASE.rstrip("/")
    json_str = json.dumps(payload, ensure_ascii=False)
    url = f"{base}{path}?json={quote(json_str)}"
    api_key = get_api_key()
    try:
        import requests
        headers = {"Api-Key": api_key, "Content-Type": "application/json"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            logger.debug("Neshan geocode HTTP %s: %s", resp.status_code, resp.text[:200])
            return None
        data = resp.json()
        if not isinstance(data, dict):
            return None
        return data
    except Exception as e:
        logger.debug("Neshan geocode failed: %s", e)
        return None
