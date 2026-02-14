# تنظیمات API نشان — کلیدها و آدرس پایه را در .env قرار دهید.
# مستندات: https://platform.neshan.org/docs/
# دو کلید: service (فراخوانی از بک‌اند)، web (برای فرانت/نقشه در صورت نیاز).

import os
from pathlib import Path

from django.conf import settings


def _env_file_paths():
    """مسیرهای ممکن برای فایل .env (ریشهٔ پروژه)."""
    paths = []
    try:
        base = getattr(settings, "BASE_DIR", None)
        if base is not None:
            paths.append(Path(base) / ".env")
    except Exception:
        pass
    # fallback: از team13/neshan/config.py دو سطح بالا = پوشهٔ team13، سه سطح = ریشهٔ پروژه
    root_candidate = Path(__file__).resolve().parent.parent.parent
    paths.append(root_candidate / ".env")
    return paths


def _read_env_file():
    """خواندن مقدار از فایل .env در ریشهٔ پروژه (بدون وابستگی به settings)."""
    out = {}
    for env_path in _env_file_paths():
        try:
            if not env_path.is_file():
                continue
            with open(env_path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        v = v.strip()
                        if "#" in v:
                            v = v.split("#", 1)[0].strip()
                        v = v.strip('"').strip("'")
                        out[k.strip()] = v
            if out:
                break
        except Exception:
            continue
    return out


def _get_setting(name, env_name, default=""):
    try:
        val = getattr(settings, name, None) or ""
    except Exception:
        val = ""
    val = (val or os.environ.get(env_name) or "").strip()
    if not val:
        _env = _read_env_file()
        val = _env.get(env_name, "").strip()
    return val or default


def get_api_key():
    """کلید سرویس نشان برای فراخوانی از بک‌اند (مسیریابی، reverse، جستجو)."""
    return _get_setting("NESHAN_API_KEY_SERVICE", "NESHAN_API_KEY_SERVICE") or _get_setting("NESHAN_API_KEY", "NESHAN_API_KEY") or os.environ.get("API_KEY", "").strip()


def get_web_key():
    """کلید وب نشان برای استفاده در فرانت (نقشه، در صورت نیاز)."""
    return _get_setting("NESHAN_API_KEY_WEB", "NESHAN_API_KEY_WEB")


def is_configured():
    """آیا حداقل یکی از کلیدهای نشان تنظیم شده است؟"""
    return bool(get_api_key() or get_web_key())


# آدرس پایهٔ API — مستندات: https://platform.neshan.org/docs/api/routing-category/routing/
NESHAN_API_BASE = "https://api.neshan.org"
# مسیریابی با ترافیک (خودرو/موتور): نوع وسیله type=car|motorcycle اجباری است.
NESHAN_DIRECTION_PATH = "/v4/direction"
# مسیریابی بدون ترافیک (فقط خودرو): https://platform.neshan.org/docs/api/routing-category/noTraffic-routing-api/
NESHAN_DIRECTION_NO_TRAFFIC_PATH = "/v4/direction/no-traffic"
# ماتریس فاصله: https://platform.neshan.org/docs/api/routing-category/distance-matrix/
NESHAN_DISTANCE_MATRIX_PATH = "/v1/distance-matrix"
NESHAN_DISTANCE_MATRIX_NO_TRAFFIC_PATH = "/v1/distance-matrix/no-traffic"
# مسیریابی فروشنده دوره‌گرد (TSP): https://platform.neshan.org/docs/api/routing-category/tsp/
NESHAN_TSP_PATH = "/v3/trip"
# محدوده در دسترس (Isochrone): https://platform.neshan.org/docs/api/routing-category/isochrone/
NESHAN_ISOCHRONE_PATH = "/v1/isochrone"
# نگاشت نقطه بر نقشه (Map Matching): https://platform.neshan.org/docs/api/routing-category/map-matching/
NESHAN_MAP_MATCHING_PATH = "/v3/map-matching"
# تبدیل نقطه به آدرس: https://platform.neshan.org/docs/api/search-category/reverse-geocoding/
NESHAN_REVERSE_PATH = "/v5/reverse"
# جستجوی مکان‌مبنا: https://platform.neshan.org/docs/api/search-category/search/
NESHAN_SEARCH_PATH = "/v1/search"
# تبدیل آدرس به مختصات: https://platform.neshan.org/docs/api/search-category/geocoding/
NESHAN_GEOCODING_PATH = "/geocoding/v1"
NESHAN_GEOCODING_PLUS_PATH = "/geocoding/v1/plus"
