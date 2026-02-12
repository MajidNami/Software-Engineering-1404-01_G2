import math
from typing import List, Optional, Dict
from datetime import datetime

from ..ports.facilities_service_port import FacilitiesServicePort
from ..models.region import Region
from ..models.search_criteria import SearchCriteria
from ..models.facility_cost_estimate import FacilityCostEstimate
from ..models.travel_info import TravelInfo, TransportMode
from ...domain.models.facility import Facility


class MockFacilitiesClient(FacilitiesServicePort):
    """Mock implementation of FacilitiesServicePort for development.
    
    This mock provides:
    - Hotels and restaurants for each region
    - Facility details for recommended places (attractions)
    - Travel info between facilities
    
    Note: The actual attractions/places of interest come from the Recommender service.
    This service provides the facility details (coordinates, hours, etc.) for those places.
    """

    MOCK_REGIONS = [
        Region(id="1", name="Tehran"),
        Region(id="2", name="Isfahan"),
        Region(id="3", name="Shiraz"),
        Region(id="4", name="Mashhad"),
        Region(id="5", name="Tabriz"),
        Region(id="6", name="Yazd"),
        Region(id="7", name="Kerman"),
        Region(id="8", name="Rasht"),
        Region(id="9", name="Kish"),
        Region(id="10", name="Qeshm"),
        Region(id="11", name="Ahvaz"),
        Region(id="12", name="Bandar Abbas"),
        Region(id="13", name="Hamadan"),
        Region(id="14", name="Qom"),
        Region(id="15", name="Kashan"),
    ]

    # Mapping of Persian names and alternative spellings to region IDs
    NAME_ALIASES = {
        # Tehran
        "tehran": "1", "تهران": "1",
        # Isfahan
        "isfahan": "2", "esfahan": "2", "اصفهان": "2",
        # Shiraz
        "shiraz": "3", "شیراز": "3",
        # Mashhad
        "mashhad": "4", "mashad": "4", "مشهد": "4",
        # Tabriz
        "tabriz": "5", "تبریز": "5",
        # Yazd
        "yazd": "6", "یزد": "6",
        # Kerman
        "kerman": "7", "کرمان": "7",
        # Rasht
        "rasht": "8", "رشت": "8",
        # Kish
        "kish": "9", "کیش": "9",
        # Qeshm
        "qeshm": "10", "قشم": "10",
        # Ahvaz
        "ahvaz": "11", "اهواز": "11",
        # Bandar Abbas
        "bandar abbas": "12", "bandarabbas": "12", "بندرعباس": "12",
        # Hamadan
        "hamadan": "13", "hamedan": "13", "همدان": "13",
        # Qom
        "qom": "14", "قم": "14",
        # Kashan
        "kashan": "15", "کاشان": "15",
    }

    # Mock facilities data - Hotels and Restaurants organized by region
    # Costs are in Rials (Iranian currency)
    MOCK_FACILITIES: Dict[str, List[Facility]] = {
        # Tehran (region_id: "1")
        "1": [
            # Hotels
            Facility(id=1001, name="هتل استقلال", facility_type="HOTEL", latitude=35.7796, longitude=51.4108,
                     cost=15000000, region_id="1", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.5, description="هتل پنج ستاره استقلال تهران"),
            Facility(id=1002, name="هتل آزادی", facility_type="HOTEL", latitude=35.7219, longitude=51.3347,
                     cost=12000000, region_id="1", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.3, description="هتل پنج ستاره آزادی"),
            Facility(id=1003, name="هتل ایبیس", facility_type="HOTEL", latitude=35.7010, longitude=51.4014,
                     cost=5000000, region_id="1", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=3.8, description="هتل سه ستاره ایبیس"),
            Facility(id=1004, name="هتل ایران", facility_type="HOTEL", latitude=35.6892, longitude=51.3890,
                     cost=2500000, region_id="1", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.0, description="هتل دو ستاره ایران"),
            # Restaurants
            Facility(id=1101, name="رستوران دیزی سرا", facility_type="RESTAURANT", latitude=35.7156, longitude=51.4194,
                     cost=800000, region_id="1", visit_duration_minutes=90, opening_hour=11, closing_hour=23,
                     tags=["food", "traditional"], rating=4.2, description="رستوران سنتی دیزی سرا"),
            Facility(id=1102, name="رستوران نایب", facility_type="RESTAURANT", latitude=35.7589, longitude=51.4103,
                     cost=1200000, region_id="1", visit_duration_minutes=90, opening_hour=12, closing_hour=24,
                     tags=["food", "kebab"], rating=4.5, description="رستوران نایب - کباب"),
            Facility(id=1103, name="فست فود سامان", facility_type="RESTAURANT", latitude=35.7012, longitude=51.4050,
                     cost=400000, region_id="1", visit_duration_minutes=45, opening_hour=10, closing_hour=23,
                     tags=["food", "fast_food"], rating=3.5, description="فست فود سامان"),
        ],
        # Isfahan (region_id: "2")
        "2": [
            # Hotels
            Facility(id=2001, name="هتل عباسی", facility_type="HOTEL", latitude=32.6539, longitude=51.6660,
                     cost=18000000, region_id="2", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury", "historic"], rating=4.8, description="هتل تاریخی عباسی - قدیمی‌ترین هتل ایران"),
            Facility(id=2002, name="هتل کوثر", facility_type="HOTEL", latitude=32.6446, longitude=51.6553,
                     cost=8000000, region_id="2", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=4.0, description="هتل کوثر اصفهان"),
            Facility(id=2003, name="هتل ستاره", facility_type="HOTEL", latitude=32.6500, longitude=51.6700,
                     cost=3000000, region_id="2", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.2, description="هتل ستاره اصفهان"),
            # Restaurants
            Facility(id=2101, name="رستوران شهرزاد", facility_type="RESTAURANT", latitude=32.6550, longitude=51.6600,
                     cost=900000, region_id="2", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "traditional"], rating=4.4, description="رستوران سنتی شهرزاد"),
            Facility(id=2102, name="سفره خانه سنتی", facility_type="RESTAURANT", latitude=32.6570, longitude=51.6680,
                     cost=600000, region_id="2", visit_duration_minutes=90, opening_hour=11, closing_hour=22,
                     tags=["food", "traditional"], rating=4.0, description="سفره خانه سنتی اصفهان"),
        ],
        # Shiraz (region_id: "3")
        "3": [
            # Hotels
            Facility(id=3001, name="هتل چمران", facility_type="HOTEL", latitude=29.6314, longitude=52.5279,
                     cost=10000000, region_id="3", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.3, description="هتل بزرگ چمران شیراز"),
            Facility(id=3002, name="هتل پارس", facility_type="HOTEL", latitude=29.6200, longitude=52.5350,
                     cost=6000000, region_id="3", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=3.9, description="هتل پارس شیراز"),
            Facility(id=3003, name="هتل ارم", facility_type="HOTEL", latitude=29.6150, longitude=52.5400,
                     cost=2000000, region_id="3", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.0, description="هتل ارم شیراز"),
            # Restaurants
            Facility(id=3101, name="رستوران شاطر عباس", facility_type="RESTAURANT", latitude=29.6250, longitude=52.5300,
                     cost=700000, region_id="3", visit_duration_minutes=90, opening_hour=11, closing_hour=23,
                     tags=["food", "traditional"], rating=4.3, description="رستوران شاطر عباس"),
            Facility(id=3102, name="رستوران هفت خوان", facility_type="RESTAURANT", latitude=29.6180, longitude=52.5380,
                     cost=1000000, region_id="3", visit_duration_minutes=90, opening_hour=12, closing_hour=24,
                     tags=["food", "traditional"], rating=4.5, description="رستوران هفت خوان"),
        ],
    }

    # Facility details for places recommended by the Recommender service
    # These are attractions/points of interest - the Recommender gives us place_ids,
    # and this mapping provides the full facility details
    PLACE_FACILITIES: Dict[str, Dict[str, Facility]] = {
        "1": {  # Tehran
            "برج_میلاد": Facility(id=1201, name="برج میلاد", facility_type="ATTRACTION", latitude=35.7448, longitude=51.3753,
                     cost=500000, region_id="1", visit_duration_minutes=120, opening_hour=9, closing_hour=22,
                     tags=["modern", "sightseeing"], rating=4.3, description="برج میلاد - نماد مدرن تهران"),
            "کاخ_گلستان": Facility(id=1202, name="کاخ گلستان", facility_type="ATTRACTION", latitude=35.6836, longitude=51.4174,
                     cost=300000, region_id="1", visit_duration_minutes=150, opening_hour=9, closing_hour=17,
                     tags=["history", "culture"], rating=4.7, description="کاخ گلستان - میراث جهانی یونسکو"),
            "پل_طبیعت": Facility(id=1203, name="پل طبیعت", facility_type="ATTRACTION", latitude=35.7635, longitude=51.4053,
                     cost=0, region_id="1", visit_duration_minutes=60, opening_hour=6, closing_hour=24,
                     tags=["nature", "modern"], rating=4.4, description="پل طبیعت - پل عابر پیاده"),
            "بازار_بزرگ_تهران": Facility(id=1204, name="بازار بزرگ تهران", facility_type="ATTRACTION", latitude=35.6762, longitude=51.4258,
                     cost=0, region_id="1", visit_duration_minutes=180, opening_hour=8, closing_hour=18,
                     tags=["shopping", "history"], rating=4.1, description="بازار بزرگ تهران"),
            "مجموعه_سعدآباد": Facility(id=1205, name="مجموعه سعدآباد", facility_type="ATTRACTION", latitude=35.8186, longitude=51.4089,
                     cost=400000, region_id="1", visit_duration_minutes=180, opening_hour=9, closing_hour=17,
                     tags=["history", "culture", "nature"], rating=4.5, description="مجموعه کاخ‌های سعدآباد"),
        },
        "2": {  # Isfahan
            "میدان_نقش_جهان": Facility(id=2201, name="میدان نقش جهان", facility_type="ATTRACTION", latitude=32.6575, longitude=51.6774,
                     cost=0, region_id="2", visit_duration_minutes=120, opening_hour=6, closing_hour=22,
                     tags=["history", "culture", "shopping"], rating=4.9, description="میدان نقش جهان - میراث جهانی"),
            "سی_و_سه_پل": Facility(id=2202, name="سی و سه پل", facility_type="ATTRACTION", latitude=32.6421, longitude=51.6648,
                     cost=0, region_id="2", visit_duration_minutes=60, opening_hour=0, closing_hour=24,
                     tags=["history", "nature"], rating=4.6, description="پل سی و سه چشمه"),
            "مسجد_شیخ_لطف_الله": Facility(id=2203, name="مسجد شیخ لطف الله", facility_type="ATTRACTION", latitude=32.6574, longitude=51.6780,
                     cost=200000, region_id="2", visit_duration_minutes=60, opening_hour=9, closing_hour=17,
                     tags=["history", "culture", "religion"], rating=4.8, description="مسجد شیخ لطف‌الله"),
            "کاخ_عالی_قاپو": Facility(id=2204, name="کاخ عالی قاپو", facility_type="ATTRACTION", latitude=32.6576, longitude=51.6765,
                     cost=250000, region_id="2", visit_duration_minutes=90, opening_hour=9, closing_hour=18,
                     tags=["history", "culture"], rating=4.5, description="کاخ عالی قاپو"),
            "کلیسای_وانک": Facility(id=2205, name="کلیسای وانک", facility_type="ATTRACTION", latitude=32.6389, longitude=51.6550,
                     cost=150000, region_id="2", visit_duration_minutes=90, opening_hour=9, closing_hour=17,
                     tags=["history", "culture", "religion"], rating=4.4, description="کلیسای وانک جلفا"),
        },
        "3": {  # Shiraz
            "حافظیه": Facility(id=3201, name="حافظیه", facility_type="ATTRACTION", latitude=29.6207, longitude=52.5549,
                     cost=150000, region_id="3", visit_duration_minutes=90, opening_hour=8, closing_hour=22,
                     tags=["history", "culture", "nature"], rating=4.8, description="آرامگاه حافظ"),
            "تخت_جمشید": Facility(id=3202, name="تخت جمشید", facility_type="ATTRACTION", latitude=29.9352, longitude=52.8908,
                     cost=500000, region_id="3", visit_duration_minutes=240, opening_hour=8, closing_hour=17,
                     tags=["history", "culture"], rating=4.9, description="تخت جمشید - میراث جهانی"),
            "ارگ_کریمخان": Facility(id=3203, name="ارگ کریمخان", facility_type="ATTRACTION", latitude=29.6109, longitude=52.5389,
                     cost=200000, region_id="3", visit_duration_minutes=90, opening_hour=8, closing_hour=18,
                     tags=["history", "culture"], rating=4.4, description="ارگ کریمخان زند"),
            "باغ_ارم": Facility(id=3204, name="باغ ارم", facility_type="ATTRACTION", latitude=29.6356, longitude=52.5203,
                     cost=100000, region_id="3", visit_duration_minutes=90, opening_hour=8, closing_hour=20,
                     tags=["nature", "history"], rating=4.5, description="باغ ارم - میراث جهانی"),
            "نارنجستان_قوام": Facility(id=3205, name="نارنجستان قوام", facility_type="ATTRACTION", latitude=29.6125, longitude=52.5458,
                     cost=150000, region_id="3", visit_duration_minutes=60, opening_hour=8, closing_hour=18,
                     tags=["history", "culture", "nature"], rating=4.3, description="خانه قوام - نارنجستان"),
        },
    }

    def __init__(self):
        """Initialize the mock client with facility lookup cache."""
        self._facility_cache: Dict[int, Facility] = {}
        # Cache hotels and restaurants
        for region_id, facilities in self.MOCK_FACILITIES.items():
            for facility in facilities:
                self._facility_cache[facility.id] = facility
        # Cache attractions from place facilities
        for region_id, places in self.PLACE_FACILITIES.items():
            for place_id, facility in places.items():
                self._facility_cache[facility.id] = facility

    def search_region(self, query: str) -> Optional[Region]:
        normalized = query.strip().lower()

        # Exact match on aliases
        if normalized in self.NAME_ALIASES:
            region_id = self.NAME_ALIASES[normalized]
            return next(r for r in self.MOCK_REGIONS if r.id == region_id)

        # Partial match on aliases
        for alias, region_id in self.NAME_ALIASES.items():
            if alias in normalized or normalized in alias:
                return next(r for r in self.MOCK_REGIONS if r.id == region_id)

        # No match found
        return None

    def find_facilities_in_area(self, criteria: SearchCriteria) -> List[Facility]:
        """Find facilities matching search criteria."""
        results = []
        for facility in self._facility_cache.values():
            # Check distance from criteria center
            distance = self._calculate_distance(
                criteria.latitude, criteria.longitude,
                facility.latitude, facility.longitude
            )
            if distance <= criteria.radius:
                if criteria.facility_type is None or facility.facility_type == criteria.facility_type:
                    results.append(facility)
        return results

    def get_cost_estimate(
        self,
        facility_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> FacilityCostEstimate:
        facility = self._facility_cache.get(facility_id)
        if facility:
            days = (end_date - start_date).days or 1
            estimated_cost = facility.cost * days
        else:
            estimated_cost = 0.0
        
        return FacilityCostEstimate(
            facility_id=facility_id,
            estimated_cost=estimated_cost,
            period_start=start_date,
            period_end=end_date
        )

    def get_facility_by_id(self, facility_id: int) -> Optional[Facility]:
        """Get a facility by its ID."""
        return self._facility_cache.get(facility_id)

    def get_facility_by_place_id(self, place_id: str, region_id: str) -> Optional[Facility]:
        """Get facility details for a place from the recommendation service."""
        places = self.PLACE_FACILITIES.get(region_id, {})
        return places.get(place_id)

    def get_hotels_in_region(self, region_id: str) -> List[Facility]:
        """Get all hotels in a region."""
        facilities = self.MOCK_FACILITIES.get(region_id, [])
        return [f for f in facilities if f.facility_type == "HOTEL"]

    def get_restaurants_in_region(self, region_id: str) -> List[Facility]:
        """Get all restaurants in a region."""
        facilities = self.MOCK_FACILITIES.get(region_id, [])
        return [f for f in facilities if f.facility_type == "RESTAURANT"]

    def get_travel_info(self, from_facility_id: int, to_facility_id: int) -> TravelInfo:
        """Get travel information between two facilities.
        
        Returns distance, time, transport mode, and estimated cost.
        """
        from_facility = self._facility_cache.get(from_facility_id)
        to_facility = self._facility_cache.get(to_facility_id)
        
        if not from_facility or not to_facility:
            # Default fallback if facilities not found
            return TravelInfo(
                from_facility_id=from_facility_id,
                to_facility_id=to_facility_id,
                distance_km=5.0,
                duration_minutes=15,
                transport_mode=TransportMode.TAXI,
                estimated_cost=200000  # Default cost
            )
        
        # Calculate distance
        distance_km = self._calculate_distance(
            from_facility.latitude, from_facility.longitude,
            to_facility.latitude, to_facility.longitude
        )
        
        # Determine transport mode, duration, and cost based on distance
        if distance_km <= 1.0:
            transport_mode = TransportMode.WALKING
            duration_minutes = int(distance_km * 12)  # ~5 km/h walking
            estimated_cost = 0  # Walking is free
        elif distance_km <= 3.0:
            transport_mode = TransportMode.WALKING
            duration_minutes = int(distance_km * 12)
            estimated_cost = 0
        elif distance_km <= 10.0:
            transport_mode = TransportMode.TAXI
            duration_minutes = int(distance_km * 3)  # ~20 km/h in city traffic
            # Taxi fare: base fare + per km
            estimated_cost = 100000 + int(distance_km * 30000)
        else:
            transport_mode = TransportMode.DRIVING
            duration_minutes = int(distance_km * 2)  # ~30 km/h average
            # Fuel + car cost estimate
            estimated_cost = int(distance_km * 15000)
        
        # Minimum duration of 5 minutes
        duration_minutes = max(5, duration_minutes)
        
        return TravelInfo(
            from_facility_id=from_facility_id,
            to_facility_id=to_facility_id,
            distance_km=round(distance_km, 2),
            duration_minutes=duration_minutes,
            transport_mode=transport_mode,
            estimated_cost=estimated_cost
        )

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula.
        
        Returns distance in kilometers.
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
