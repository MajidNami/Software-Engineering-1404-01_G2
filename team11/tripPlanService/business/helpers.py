import math
from typing import List, Dict, Optional

# External services - will be implemented by Mohammad Hossein
from externalServices.grpc.services.facility_client import FacilityClient
from externalServices.grpc.services.recommendation_client import RecommendationClient


class DestinationSuggester:
    """
    پیشنهاد مکان‌های بازدیدی
    """

    def __init__(self):
        self.facility_client = FacilityClient()
        self.recom_client = RecommendationClient()

    def get_destinations(
            self,
            province: str,
            city: Optional[str],
            interests: List[str],
            budget_level: str,
            num_days: int
    ) -> List[Dict]:
        """
        Get list of suggested destinations

        Returns:
            List of place dictionaries ranked by relevance
        """

        # 1. Get places from Facility Service
        categories = self._map_interests_to_categories(interests)

        all_places = self.facility_client.search_places(
            province=province,
            city=city,
            categories=categories,
            budget_level=budget_level,
            limit=50
        )

        if not all_places:
            return []

        # 2. Filter by budget
        filtered_places = self._filter_by_budget(all_places, budget_level)

        # 3. Rank by recommendation service
        ranked_places = self.recom_client.rank_places(
            places=filtered_places,
            user_interests=interests
        )

        # 4. Return enough places for all days
        num_needed = num_days * 5  # 5 activities per day
        return ranked_places[:num_needed]

    def _map_interests_to_categories(self, interests: List[str]) -> List[str]:
        """
        Map user interests to place categories

        Example:
        ['تاریخی', 'فرهنگی'] → ['HISTORICAL', 'CULTURAL', 'RELIGIOUS']
        """
        mapping = {
            'تاریخی': ['HISTORICAL', 'RELIGIOUS', 'CULTURAL'],
            'فرهنگی': ['CULTURAL', 'HISTORICAL'],
            'طبیعت': ['NATURAL', 'RECREATIONAL'],
            'خانوادگی': ['RECREATIONAL', 'NATURAL'],
            'مذهبی': ['RELIGIOUS', 'HISTORICAL'],
            'غذا': ['DINING']
        }

        categories = []
        for interest in interests:
            categories.extend(mapping.get(interest, []))

        categories = list(set(categories))
        return categories

    def _filter_by_budget(self, places: List[Dict], budget_level: str) -> List[Dict]:
        """Filter places by budget level"""

        budget_ranges = {
            'ECONOMY': ['FREE', 'BUDGET'],
            'MEDIUM': ['FREE', 'BUDGET', 'MODERATE'],
            'LUXURY': ['FREE', 'BUDGET', 'MODERATE', 'EXPENSIVE', 'LUXURY'],
            'UNLIMITED': ['FREE', 'BUDGET', 'MODERATE', 'EXPENSIVE', 'LUXURY']
        }

        allowed_tiers = budget_ranges.get(budget_level, ['FREE', 'BUDGET', 'MODERATE'])

        return [
            place for place in places
            if place.get('price_tier', 'FREE') in allowed_tiers
        ]


class AlternativesProvider:
    """
    پیشنهاد مکان‌های جایگزین (برای API سیدعلی)
    """


    def __init__(self):
        self.facility_client = FacilityClient()

    def get_alternatives(
            self,
            original_place_id: str,
            province: str,
            city: Optional[str],
            category: str,
            max_results: int = 5
    ) -> List[Dict]:
        """
        Find alternative places similar to the original

        Returns:
            List of up to 5 alternative places
        """

        # 1. Get original place info
        original = self.facility_client.get_place_by_id(original_place_id)

        if not original:
            return []

        # 2. Search for similar places
        alternatives = self.facility_client.search_places(
            province=province,
            city=city,
            categories=[category],
            limit=20
        )

        # 3. Remove original from list
        alternatives = [
            p for p in alternatives
            if p['id'] != original_place_id
        ]

        # 4. Rank by distance from original
        if original.get('lat') and original.get('lng'):
            alternatives = self._rank_by_distance(
                alternatives,
                original['lat'],
                original['lng']
            )

        return alternatives[:max_results]

    def _rank_by_distance(
            self,
            places: List[Dict],
            ref_lat: float,
            ref_lng: float
    ) -> List[Dict]:
        """Rank places by distance from reference point"""

        def haversine(lat1, lon1, lat2, lon2):
            """Calculate distance between two points in km"""
            R = 6371  # Earth radius in kilometers
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (math.sin(dlat / 2) ** 2 +
                 math.cos(math.radians(lat1)) *
                 math.cos(math.radians(lat2)) *
                 math.sin(dlon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        # Calculate distance for each place
        for place in places:
            if place.get('lat') and place.get('lng'):
                place['distance'] = haversine(
                    ref_lat, ref_lng,
                    place['lat'], place['lng']
                )
            else:
                place['distance'] = float('inf')

        # Sort by distance
        return sorted(places, key=lambda p: p['distance'])


class AvailabilityChecker:
    """
    چک کردن availability مکان‌ها
    """

    def __init__(self):
        self.facility_client = FacilityClient()

    def check_place_availability(
            self,
            place_id: str,
            date: str,
            start_time: str,
            end_time: str
    ) -> Dict:
        """
        Check if a place is available at the specified time

        Args:
            place_id: Place ID
            date: Date in YYYY-MM-DD format
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format

        Returns:
            {
                'is_available': bool,
                'reason': str,
                'suggested_times': List[str]
            }
        """

        # Use Facility Service to check availability
        return self.facility_client.check_availability(
            place_id=place_id,
            date=date,
            start_time=start_time,
            end_time=end_time
        )


def validate_time_reschedule(item, new_start_time=None, new_end_time=None):
    """
    Validate if an item can be rescheduled to new time slot.

    Checks:
    1. Item is not locked
    2. Item is not in the past
    3. Place is available at new time
    4. Time constraints (15-minute intervals, minimum 60 minutes)

    Args:
        item: TripItem instance
        new_start_time: New start time (None = keep current)
        new_end_time: New end time (None = keep current)

    Returns:
        {
            "valid": bool,
            "error": str,  # if not valid
            "availability": dict  # from check_place_availability
        }
    """
    from datetime import datetime, timedelta, date

    # Use existing times if not changing
    start = new_start_time or item.start_time
    end = new_end_time or item.end_time

    # Check 1: Is locked?
    if item.is_locked:
        return {
            "valid": False,
            "error": "این آیتم قفل شده است و نمی‌توان زمان آن را تغییر داد",
            "availability": {}
        }

    # Check 2: Is past event?
    event_datetime = datetime.combine(item.day.specific_date, end)
    if event_datetime < datetime.now():
        return {
            "valid": False,
            "error": "نمی‌توان زمان آیتم‌های گذشته را تغییر داد",
            "availability": {}
        }

    # Check 3: Time constraints (15-minute intervals)
    if start.minute % 15 != 0 or end.minute % 15 != 0:
        return {
            "valid": False,
            "error": "زمان باید مضرب 15 دقیقه باشد",
            "availability": {}
        }

    # Check 4: Minimum duration (60 minutes)
    start_dt = datetime.combine(date.today(), start)
    end_dt = datetime.combine(date.today(), end)
    duration_minutes = (end_dt - start_dt).total_seconds() / 60

    if duration_minutes < 60:
        return {
            "valid": False,
            "error": "مدت زمان حداقل باید 60 دقیقه باشد",
            "availability": {}
        }

    # Check 5: Place availability
    # TODO: Integration with Mohammad Hossein's Facility Service
    # When ready, use the actual AvailabilityChecker class above
    availability = {
        "is_available": True,
        "reason": "",
        "suggested_times": []
    }

    # Uncomment when Facility Service is ready:
    # checker = AvailabilityChecker()
    # availability = checker.check_place_availability(
    #     place_id=item.place_ref_id,
    #     date=item.day.specific_date.isoformat(),
    #     start_time=start.isoformat(),
    #     end_time=end.isoformat()
    # )

    if not availability.get("is_available", True):
        return {
            "valid": False,
            "error": f"مکان در این بازه زمانی بسته است. {availability.get('reason', '')}",
            "availability": availability
        }

    return {
        "valid": True,
        "error": "",
        "availability": availability
    }
