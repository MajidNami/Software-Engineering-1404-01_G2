"""
HTTP implementation of FacilitiesServicePort calling Team 4 Facilities API.
Uses api_integration_guide.json: SearchRegions, GetPlacesInRegion, GetNearbyPlaces, GetPlaceByIds.
GetTravelEstimates is not implemented by the API; we compute a local estimate.
"""
import math
import logging
from typing import List, Optional
from datetime import datetime

import requests

from ..ports.facilities_service_port import FacilitiesServicePort
from ..models.region import Region
from ..models.search_criteria import SearchCriteria
from ..models.facility_cost_estimate import FacilityCostEstimate
from ..models.travel_info import TravelInfo, TransportMode
from ...domain.models.facility import Facility

logger = logging.getLogger(__name__)

# Map our region_id (e.g. "1", "2") to city/province name for Team4 API
REGION_ID_TO_CITY_NAME = {
    "1": "تهران",
    "2": "اصفهان",
    "3": "شیراز",
    "4": "مشهد",
    "5": "تبریز",
    "6": "یزد",
    "7": "کرمان",
    "8": "رشت",
    "9": "کیش",
    "10": "قشم",
    "11": "اهواز",
    "12": "بندرعباس",
    "13": "همدان",
    "14": "قم",
    "15": "کاشان",
}


class HttpFacilitiesClient(FacilitiesServicePort):
    """
    HTTP implementation for the Facilities Service (Team 4).
    Maps the external API to the internal Facility/Region/TravelInfo models.
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()

    def _get(self, path: str, params: Optional[dict] = None) -> Optional[dict]:
        url = f"{self.base_url}{path}"
        try:
            r = self._session.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.warning("Facilities API GET %s failed: %s", path, e)
            return None

    def _post(self, path: str, json: Optional[dict] = None, params: Optional[dict] = None) -> Optional[dict]:
        url = f"{self.base_url}{path}"
        try:
            r = self._session.post(url, json=json or {}, params=params, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.warning("Facilities API POST %s failed: %s", path, e)
            return None

    def search_region(self, query: str) -> Optional[Region]:
        """Search for a region by name. GET /team4/api/regions/search/?query=..."""
        data = self._get("/team4/api/regions/search/", params={"query": query.strip()})
        if not data or not isinstance(data, list):
            return None
        first = data[0] if data else None
        if not first:
            return None
        return Region(id=str(first.get("id", "")), name=first.get("name", ""))

    def find_facilities_in_area(self, criteria: SearchCriteria) -> List[Facility]:
        """Find facilities in area. Uses GetNearbyPlaces (lat, lng, radius in meters)."""
        params = {
            "lat": criteria.latitude,
            "lng": criteria.longitude,
            "radius": int(criteria.radius),
            "page_size": 50,
        }
        if criteria.facility_type:
            c = criteria.facility_type.upper()
            if c == "HOTEL":
                params["categories"] = "hotel"
            elif c == "RESTAURANT":
                params["categories"] = "restaurant"
        data = self._get("/team4/api/facilities/nearby/", params=params)
        if not data:
            return []
        results = data.get("results") or []
        facilities = []
        for item in results:
            place_data = item.get("place") or item
            fac = self._map_place_to_facility(place_data)
            if fac:
                if not criteria.facility_type or fac.facility_type == criteria.facility_type.upper():
                    facilities.append(fac)
        return facilities

    def get_cost_estimate(
        self,
        facility_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> FacilityCostEstimate:
        """API has no cost estimate endpoint; derive from facility price or return zero."""
        facility = self.get_facility_by_id(facility_id)
        if facility and facility.cost and facility.cost > 0:
            days = max(1, (end_date - start_date).days)
            estimated_cost = float(facility.cost) * days
        else:
            estimated_cost = 0.0
        return FacilityCostEstimate(
            facility_id=facility_id,
            estimated_cost=estimated_cost,
            period_start=start_date,
            period_end=end_date,
        )

    def get_facility_by_id(self, facility_id: int) -> Optional[Facility]:
        """Get a facility by ID. GET /team4/api/facilities/{fac_id}/"""
        data = self._get(f"/team4/api/facilities/{facility_id}/")
        if not data:
            return None
        return self._map_detail_to_facility(data)

    def get_facility_by_place_id(self, place_id: str, region_id: str) -> Optional[Facility]:
        """
        Get facility for a place_id from the recommendation service.
        Team4 uses integer fac_id; recommendation uses string place_id. Try by ID first; else search in region.
        """
        if not place_id:
            return None
        if place_id.isdigit():
            return self.get_facility_by_id(int(place_id))
        city = REGION_ID_TO_CITY_NAME.get(region_id) or region_id
        data = self._post("/team4/api/facilities/search/", json={"city": city}, params={"page": 1, "page_size": 50})
        if not data:
            return None
        results = data.get("results") or []
        slug = place_id.replace("-", " ").replace("_", " ")
        for item in results:
            name_fa = (item.get("name_fa") or "").replace(" ", "")
            name_en = (item.get("name_en") or "").lower().replace(" ", "")
            if slug.replace(" ", "") in name_fa or slug.lower().replace(" ", "") in name_en:
                fac = self._map_place_to_facility(item)
                if fac:
                    return fac
        return None

    def get_hotels_in_region(self, region_id: str) -> List[Facility]:
        """Get hotels in region. POST /team4/api/facilities/search/ with category=hotel."""
        return self._get_places_in_region(region_id, "hotel")

    def get_restaurants_in_region(self, region_id: str) -> List[Facility]:
        """Get restaurants in region. POST /team4/api/facilities/search/ with category=restaurant."""
        return self._get_places_in_region(region_id, "restaurant")

    def _get_places_in_region(self, region_id: str, category: str) -> List[Facility]:
        city = REGION_ID_TO_CITY_NAME.get(region_id) or region_id
        data = self._post("/team4/api/facilities/search/", json={"city": city, "category": category}, params={"page": 1, "page_size": 50})
        if not data:
            return []
        results = data.get("results") or []
        return [f for f in (self._map_place_to_facility(item) for item in results) if f]

    def get_travel_info(self, from_facility_id: int, to_facility_id: int) -> TravelInfo:
        """GetTravelEstimates not implemented by API; compute locally from facility coordinates."""
        from_f = self.get_facility_by_id(from_facility_id)
        to_f = self.get_facility_by_id(to_facility_id)
        if not from_f or not to_f:
            return TravelInfo(
                from_facility_id=from_facility_id,
                to_facility_id=to_facility_id,
                distance_km=5.0,
                duration_minutes=15,
                transport_mode=TransportMode.TAXI,
                estimated_cost=200000.0,
            )
        distance_km = self._haversine_km(from_f.latitude, from_f.longitude, to_f.latitude, to_f.longitude)
        if distance_km <= 1.0:
            transport_mode = TransportMode.WALKING
            duration_minutes = max(5, int(distance_km * 12))
            estimated_cost = 0.0
        elif distance_km <= 10.0:
            transport_mode = TransportMode.TAXI
            duration_minutes = max(5, int(distance_km * 3))
            estimated_cost = 100000.0 + distance_km * 30000
        else:
            transport_mode = TransportMode.DRIVING
            duration_minutes = max(5, int(distance_km * 2))
            estimated_cost = distance_km * 15000
        return TravelInfo(
            from_facility_id=from_facility_id,
            to_facility_id=to_facility_id,
            distance_km=round(distance_km, 2),
            duration_minutes=duration_minutes,
            transport_mode=transport_mode,
            estimated_cost=float(int(estimated_cost)),
        )

    @staticmethod
    def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def _normalize_category(raw: str) -> str:
        """Map API category (e.g. هتل, hotel) to our facility_type (HOTEL, RESTAURANT, ATTRACTION)."""
        r = (raw or "").strip().lower()
        if "hotel" in r or "هتل" in raw:
            return "HOTEL"
        if "restaurant" in r or "رستوران" in raw or "غذا" in raw:
            return "RESTAURANT"
        return "ATTRACTION"

    def _map_place_to_facility(self, place_data: dict) -> Optional[Facility]:
        """Map API place or search result to Facility."""
        try:
            coords = place_data.get("location") or {}
            coord_list = coords.get("coordinates", [0.0, 0.0])
            lng, lat = float(coord_list[0]), float(coord_list[1])
            name = place_data.get("name_fa") or place_data.get("name_en") or "Unknown"
            fac_id = int(place_data.get("fac_id", 0))
            raw_cat = place_data.get("category", "general")
            if isinstance(raw_cat, dict):
                raw_cat = raw_cat.get("name_en") or raw_cat.get("name_fa") or "general"
            category = self._normalize_category(str(raw_cat))
            cost = self._price_tier_to_cost(place_data.get("price_tier", "unknown"))
            if cost == 0 and place_data.get("price_from"):
                pf = place_data["price_from"]
                if isinstance(pf, dict) and "amount" in pf:
                    cost = float(pf["amount"])
            try:
                rating = float(place_data.get("avg_rating", 0) or 0)
            except (TypeError, ValueError):
                rating = 0.0
            amenities = place_data.get("amenities") or []
            tags = [a.get("name_en") or a.get("name_fa") for a in amenities if isinstance(a, dict)]
            tags = [t for t in tags if t]
            return Facility(
                name=name,
                facility_type=category,
                latitude=lat,
                longitude=lng,
                cost=cost,
                id=fac_id,
                region_id=None,
                description=place_data.get("description_fa") or place_data.get("description_en"),
                visit_duration_minutes=60,
                opening_hour=8,
                closing_hour=22,
                tags=tags,
                rating=rating,
            )
        except Exception as e:
            logger.debug("Map place to facility failed: %s", e)
            return None

    def _map_detail_to_facility(self, data: dict) -> Optional[Facility]:
        """Map GET /facilities/{id}/ detail response to Facility."""
        try:
            coords = data.get("location") or {}
            coord_list = coords.get("coordinates", [0.0, 0.0])
            lng, lat = float(coord_list[0]), float(coord_list[1])
            name = data.get("name_fa") or data.get("name_en") or "Unknown"
            fac_id = int(data.get("fac_id", 0))
            raw_cat = data.get("category")
            if isinstance(raw_cat, dict):
                raw_cat = raw_cat.get("name_en") or raw_cat.get("name_fa") or "general"
            else:
                raw_cat = raw_cat or "general"
            category = self._normalize_category(str(raw_cat))
            cost = self._price_tier_to_cost(data.get("price_tier", "unknown"))
            for p in data.get("pricing") or []:
                if isinstance(p, dict) and p.get("price") is not None:
                    try:
                        cost = float(p["price"])
                        break
                    except (TypeError, ValueError):
                        pass
            try:
                rating = float(data.get("avg_rating", 0) or 0)
            except (TypeError, ValueError):
                rating = 0.0
            amenities = data.get("amenities") or []
            tags = [a.get("name_en") or a.get("name_fa") for a in amenities if isinstance(a, dict)]
            tags = [t for t in tags if t]
            return Facility(
                name=name,
                facility_type=category,
                latitude=lat,
                longitude=lng,
                cost=cost,
                id=fac_id,
                region_id=None,
                description=data.get("description_fa") or data.get("description_en"),
                visit_duration_minutes=60,
                opening_hour=8,
                closing_hour=22,
                tags=tags,
                rating=rating,
            )
        except Exception as e:
            logger.debug("Map detail to facility failed: %s", e)
            return None

    @staticmethod
    def _price_tier_to_cost(price_tier: str) -> float:
        tier_map = {
            "free": 0.0,
            "budget": 500000.0,
            "moderate": 2000000.0,
            "expensive": 5000000.0,
            "luxury": 10000000.0,
            "unknown": 0.0,
        }
        return tier_map.get((price_tier or "").lower(), 0.0)
