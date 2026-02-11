from typing import List, Dict, Optional
from .externalServices.facility_client import FacilityClient
from .externalServices.recommendation_client import RecommendationClient


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
        دریافت لیست مکان‌های پیشنهادی

        Returns:
            لیستی از Dicts با فیلدهای: id, title, category, lat, lng, address
        """

        # 1. دریافت لیست مکان‌ها از Facility Service
        all_places = self.facility_client.search_places(
            province=province,
            city=city,
            categories=self._map_interests_to_categories(interests)
        )

        # 2. فیلتر بر اساس budget_level
        filtered_places = self._filter_by_budget(all_places, budget_level)

        # 3. رتبه‌بندی با Recommendation Service
        ranked_places = self.recom_client.rank_places(
            places=filtered_places,
            user_interests=interests
        )

        # 4. انتخاب تعداد مناسب (برای num_days روز)
        # فرض: هر روز 3-4 مکان بازدیدی
        num_needed = num_days * 4
        return ranked_places[:num_needed]

    def _map_interests_to_categories(self, interests: List[str]) -> List[str]:
        """
        تبدیل interests کاربر به categories در Facility Service

        مثال:
        ['تاریخی', 'فرهنگی'] → ['موزه', 'بنای تاریخی', 'آثارباستانی']
        """
        mapping = {
            'تاریخی': ['موزه', 'بنای تاریخی', 'آثارباستانی'],
            'فرهنگی': ['تئاتر', 'سینما', 'کتابخانه', 'گالری'],
            'طبیعت': ['پارک', 'جنگل', 'کوهستان', 'دریا'],
            'خانوادگی': ['پارک', 'تفریحگاه', 'باغ']
        }

        categories = []
        for interest in interests:
            categories.extend(mapping.get(interest, []))

        return list(set(categories))  # حذف تکراری‌ها

    def _filter_by_budget(self, places: List[Dict], budget_level: str) -> List[Dict]:
        """
        فیلتر مکان‌ها بر اساس سطح بودجه
        """
        budget_ranges = {
            'LOW': (0, 200000),
            'MEDIUM': (0, 500000),
            'HIGH': (0, float('inf'))
        }

        min_cost, max_cost = budget_ranges.get(budget_level, (0, float('inf')))

        return [
            place for place in places
            if min_cost <= place.get('entry_fee', 0) <= max_cost
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
        category: str
    ) -> List[Dict]:
        """
        پیدا کردن مکان‌های مشابه برای جایگزینی

        طبق User Story: کاربر می‌تونه یک Item رو با یکی از Alternatives جایگزین کنه
        """

        # 1. دریافت اطلاعات مکان اصلی
        original = self.facility_client.get_place_by_id(original_place_id)

        # 2. جستجوی مکان‌های همون دسته‌بندی
        alternatives = self.facility_client.search_places(
            province=province,
            city=city,
            categories=[category]
        )

        # 3. حذف مکان اصلی از لیست
        alternatives = [p for p in alternatives if p['id'] != original_place_id]

        # 4. رتبه‌بندی بر اساس فاصله از مکان اصلی
        if original and 'lat' in original and 'lng' in original:
            alternatives = self._rank_by_distance(
                alternatives,
                original['lat'],
                original['lng']
            )

        # 5. برگشت 5 گزینه برتر
        return alternatives[:5]

    def _rank_by_distance(
        self,
        places: List[Dict],
        ref_lat: float,
        ref_lng: float
    ) -> List[Dict]:
        """
        رتبه‌بندی مکان‌ها بر اساس فاصله
        """
        import math

        def haversine(lat1, lon1, lat2, lon2):
            """محاسبه فاصله بین دو نقطه"""
            R = 6371  # شعاع زمین به کیلومتر
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (math.sin(dlat / 2) ** 2 +
                 math.cos(math.radians(lat1)) *
                 math.cos(math.radians(lat2)) *
                 math.sin(dlon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        for place in places:
            place['distance'] = haversine(
                ref_lat, ref_lng,
                place.get('lat', 0),
                place.get('lng', 0)
            )

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
        چک کردن آیا مکان در این زمان باز است

        Returns:
            {
                'is_available': bool,
                'reason': str (اگه available نباشه)
            }
        """

        # دریافت اطلاعات مکان از Facility Service
        place = self.facility_client.get_place_by_id(place_id)

        if not place:
            return {'is_available': False, 'reason': 'مکان یافت نشد'}

        # چک کردن opening_hours
        opening_hours = place.get('opening_hours', {})

        # TODO: پیاده‌سازی دقیق‌تر با توجه به ساختار opening_hours
        # فعلاً فرض می‌کنیم همیشه available است

        return {'is_available': True}
