
# business/generators.py
from typing import List, Dict, Optional
from datetime import date, timedelta, time
from data.models import Trip, TripDay, TripItem
from .helpers import DestinationSuggester
from .externalServices.facility_client import FacilityClient


class TripGenerator:
    """
    الگوریتم اصلی ساخت Trip
    """

    def __init__(self):
        self.suggester = DestinationSuggester()
        self.facility_client = FacilityClient()

    def generate(
        self,
        province: str,
        city: Optional[str],
        interests: List[str],
        budget_level: str,
        start_date: date,
        end_date: Optional[date] = None
    ) -> Trip:
        """
        الگوریتم اصلی ساخت Trip

        Args:
            province: استان (اجباری)
            city: شهر (اختیاری)
            interests: علاقه‌مندی‌ها (لیست)
            budget_level: سطح بودجه (LOW/MEDIUM/HIGH)
            start_date: تاریخ شروع (اجباری)
            end_date: تاریخ پایان (اختیاری)

        Returns:
            Trip: یک Trip کامل با Days و Items
        """

        # 1. محاسبه Duration
        if end_date is None:
            # اگه end_date نداریم، پیش‌فرض 3 روز
            end_date = start_date + timedelta(days=2)

        duration_days = (end_date - start_date).days + 1

        # 2. دریافت لیست مکان‌های پیشنهادی
        suggested_places = self.suggester.get_destinations(
            province=province,
            city=city,
            interests=interests,
            budget_level=budget_level,
            num_days=duration_days
        )

        # 3. ساخت Trip خالی
        trip = Trip.objects.create(
            title=f"سفر به {city or province}",
            province=province,
            city=city,
            start_date=start_date,
            end_date=end_date,
            budget_level=budget_level,
            interests=interests,
            status='DRAFT'
        )

        # 4. پر کردن روزها
        current_date = start_date
        for day_index in range(1, duration_days + 1):
            self._generate_day(
                trip=trip,
                day_index=day_index,
                date=current_date,
                suggested_places=suggested_places,
                budget_level=budget_level
            )
            current_date += timedelta(days=1)

        # 5. محاسبه هزینه کل
        trip.recalculate_cost()
        trip.status = 'ACTIVE'
        trip.save()

        return trip

    def _generate_day(
        self,
        trip: Trip,
        day_index: int,
        date: date,
        suggested_places: List[Dict],
        budget_level: str
    ):
        """
        پر کردن یک روز با Items

        طبق Voice Note:
        - هر روز شامل چندین VISIT و یک STAY
        - حداقل duration: 1 ساعت
        """

        # ساخت Day
        trip_day = TripDay.objects.create(
            trip=trip,
            day_index=day_index,
            date=date
        )

        # زمان شروع روز: 9 صبح
        current_time = time(9, 0)

        # 1. محل صبحانه (60 دقیقه)
        breakfast = self._find_place(suggested_places, 'رستوران', 'VISIT')
        if breakfast:
            current_time = self._add_item(
                trip_day=trip_day,
                place_data=breakfast,
                start_time=current_time,
                duration_hours=1,
                item_type='VISIT'
            )

        # 2. مکان بازدیدی 1 (2-3 ساعت)
        visit1 = self._find_place(suggested_places, interests_match=True, item_type='VISIT')
        if visit1:
            current_time = self._add_item(
                trip_day=trip_day,
                place_data=visit1,
                start_time=current_time,
                duration_hours=2.5,
                item_type='VISIT'
            )

        # 3. ناهار (60 دقیقه)
        lunch = self._find_place(suggested_places, 'رستوران', 'VISIT')
        if lunch:
            current_time = self._add_item(
                trip_day=trip_day,
                place_data=lunch,
                start_time=current_time,
                duration_hours=1,
                item_type='VISIT'
            )

        # 4. مکان بازدیدی 2 (2-3 ساعت)
        visit2 = self._find_place(suggested_places, interests_match=True, item_type='VISIT')
        if visit2:
            current_time = self._add_item(
                trip_day=trip_day,
                place_data=visit2,
                start_time=current_time,
                duration_hours=2.5,
                item_type='VISIT'
            )

        # 5. شام (60 دقیقه)
        dinner = self._find_place(suggested_places, 'رستوران', 'VISIT')
        if dinner:
            current_time = self._add_item(
                trip_day=trip_day,
                place_data=dinner,
                start_time=current_time,
                duration_hours=1,
                item_type='VISIT'
            )

        # 6. محل اقامت (11 ساعت = شب تا صبح)
        stay = self._find_place(suggested_places, 'هتل', 'STAY')
        if stay:
            self._add_item(
                trip_day=trip_day,
                place_data=stay,
                start_time=current_time,
                duration_hours=11,
                item_type='STAY'
            )

    def _add_item(
        self,
        trip_day: TripDay,
        place_data: Dict,
        start_time: time,
        duration_hours: float,
        item_type: str
    ) -> time:
        """
        افزودن یک Item به TripDay

        Returns:
            زمان پایان این Item (برای شروع Item بعدی)
        """
        from datetime import datetime, timedelta

        # محاسبه end_time
        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = start_dt + timedelta(hours=duration_hours)
        end_time = end_dt.time()

        # ساخت Item
        TripItem.objects.create(
            trip_day=trip_day,
            item_type=item_type,
            place_id=place_data['id'],
            title=place_data['title'],
            category=place_data.get('category'),
            address_summary=place_data.get('address'),
            lat=place_data.get('lat'),
            lng=place_data.get('lng'),
            start_time=start_time,
            end_time=end_time,
            estimated_cost=self._estimate_cost(place_data, duration_hours)
        )

        return end_time

    def _find_place(
        self,
        places: List[Dict],
        category: Optional[str] = None,
        item_type: Optional[str] = None,
        interests_match: bool = False
    ) -> Optional[Dict]:
        """
        پیدا کردن یک مکان مناسب از لیست

        TODO: پیاده‌سازی دقیق‌تر با فیلترهای بیشتر
        """
        for place in places:
            if category and place.get('category') == category:
                return place
            if interests_match:
                # چک کردن match با interests
                return place

        return places[0] if places else None

    def _estimate_cost(self, place_data: Dict, duration_hours: float) -> float:
        """
        تخمین هزینه بر اساس نوع مکان و مدت زمان

        TODO: پیاده‌سازی دقیق‌تر با توجه به budget_level
        """
        base_cost = place_data.get('entry_fee', 0)
        return base_cost
