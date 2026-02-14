# ماژول اتصال به APIهای نشان (neshan.ir / platform.neshan.org)
# کلید و endpointها را در config تنظیم کنید؛ سپس از توابع این پکیج در views و geo_utils استفاده می‌شود.

from .config import get_api_key, is_configured
from .routing import fetch_route_eta, fetch_route_eta_no_traffic, fetch_route_eta_pedestrian
from .geocoding import geocode, reverse_geocode, reverse_geocode_address
from .search import search_autocomplete, search_count, search_response
from .tsp import fetch_tsp
from .distance_matrix import fetch_distance_matrix
from .isochrone import fetch_isochrone
from .map_matching import fetch_map_matching

__all__ = [
    "get_api_key",
    "is_configured",
    "fetch_route_eta",
    "fetch_route_eta_no_traffic",
    "fetch_route_eta_pedestrian",
    "fetch_tsp",
    "fetch_distance_matrix",
    "fetch_isochrone",
    "fetch_map_matching",
    "geocode",
    "reverse_geocode",
    "reverse_geocode_address",
    "search_autocomplete",
    "search_count",
    "search_response",
]
