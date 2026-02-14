
"""
Trip Generator - Main algorithm for creating trips
"""
from typing import List, Dict, Optional
from datetime import date, timedelta, time, datetime
from decimal import Decimal

# Django imports
from data.models import Trip, TripDay, TripItem
from django.contrib.auth.models import User

# Local imports
from .helpers import DestinationSuggester
from externalServices.grpc.services.facility_client import FacilityClient


class TripGenerator:
    """
    Main algorithm for generating trip plans
    """

    def __init__(self):
        self.suggester = DestinationSuggester()
        self.facility_client = FacilityClient()

    def generate(
            self,
            province,
            city=None,
            interests=None,
            budget_level='MEDIUM',
            start_date=None,
            end_date=None,
            daily_available_hours=8,
            travel_style='SOLO',
            user_id=None
    ):
        """
        Generate a complete trip plan
        """

        # 1. Calculate duration
        if end_date is None:
            end_date = start_date + timedelta(days=2)  # Default 3 days

        duration_days = (end_date - start_date).days + 1

        # 2. Get suggested places
        suggested_places = self.suggester.get_destinations(
            province=province,
            city=city,
            interests=interests,
            budget_level=budget_level,
            num_days=duration_days
        )

        if not suggested_places:
            raise ValueError("No places found for the given criteria")

        # 3. Create Trip object
        trip = Trip.objects.create(
            title=f"سفر به {city or province}",
            province=province,
            city=city,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days,
            budget_level=budget_level,
            daily_available_hours=daily_available_hours,
            travel_style=travel_style,
            generation_strategy='MIXED',
            status='DRAFT',
            user_id=user_id,
        )

        # 4. Generate days
        current_date = start_date
        place_index = 0

        for day_index in range(1, duration_days + 1):
            place_index = self._generate_day(
                trip=trip,
                day_index=day_index,
                date=current_date,
                suggested_places=suggested_places,
                budget_level=budget_level,
                place_index=place_index
            )
            current_date += timedelta(days=1)

        # 5. Calculate total cost
        self._calculate_trip_cost(trip)

        trip.status = 'FINALIZED'
        trip.save()

        return trip

    def _generate_day(
            self,
            trip: Trip,
            day_index: int,
            date: date,
            suggested_places: List[Dict],
            budget_level: str,
            place_index: int
    ) -> int:
        """
        Generate items for one day

        Returns:
            Updated place_index for next day
        """

        # Create TripDay
        trip_day = TripDay.objects.create(
            trip=trip,
            day_index=day_index,
            specific_date=date
        )

        current_time = time(9, 0)  # Start at 9 AM
        sort_order = 0
        used_place_ids = set()  # Bug 12 fix: track used places per day

        # 1. Breakfast (1 hour)
        breakfast = self._find_place(suggested_places, category='DINING', place_index=place_index, used_ids=used_place_ids)
        if breakfast:
            current_time = self._add_item(
                trip_day=trip_day,
                place_data=breakfast,
                start_time=current_time,
                duration_hours=1,
                item_type='VISIT',
                sort_order=sort_order
            )
            sort_order += 1
            place_index += 1
            used_place_ids.add(breakfast.get('id'))

        # 2. Morning activity (2-3 hours)
        morning_place = self._find_place(
            suggested_places,
            exclude_category='DINING',
            place_index=place_index,
            used_ids=used_place_ids
        )
        if morning_place:
            current_time = self._add_item(
                trip_day=trip_day,
                place_data=morning_place,
                start_time=current_time,
                duration_hours=2.5,
                item_type='VISIT',
                sort_order=sort_order
            )
            sort_order += 1
            place_index += 1
            used_place_ids.add(morning_place.get('id'))

        # 3. Lunch (1 hour)
        lunch = self._find_place(suggested_places, category='DINING', place_index=place_index, used_ids=used_place_ids)
        if lunch:
            current_time = self._add_item(
                trip_day=trip_day,
                place_data=lunch,
                start_time=current_time,
                duration_hours=1,
                item_type='VISIT',
                sort_order=sort_order
            )
            sort_order += 1
            place_index += 1
            used_place_ids.add(lunch.get('id'))

        # 4. Afternoon activity (2-3 hours)
        afternoon_place = self._find_place(
            suggested_places,
            exclude_category='DINING',
            place_index=place_index,
            used_ids=used_place_ids
        )
        if afternoon_place:
            current_time = self._add_item(
                trip_day=trip_day,
                place_data=afternoon_place,
                start_time=current_time,
                duration_hours=2.5,
                item_type='VISIT',
                sort_order=sort_order
            )
            sort_order += 1
            place_index += 1
            used_place_ids.add(afternoon_place.get('id'))

        # 5. Dinner (1 hour)
        dinner = self._find_place(suggested_places, category='DINING', place_index=place_index, used_ids=used_place_ids)
        if dinner:
            current_time = self._add_item(
                trip_day=trip_day,
                place_data=dinner,
                start_time=current_time,
                duration_hours=1,
                item_type='VISIT',
                sort_order=sort_order
            )
            sort_order += 1
            place_index += 1
            used_place_ids.add(dinner.get('id'))

        # 6. Accommodation (overnight)
        # Bug 11 fix: use place_index instead of hardcoded 0
        hotel = self._find_place(suggested_places, category='STAY', place_index=place_index, used_ids=used_place_ids)
        if hotel:
            self._add_item(
                trip_day=trip_day,
                place_data=hotel,
                start_time=current_time,
                duration_hours=11,  # 11 hours overnight
                item_type='STAY',
                sort_order=sort_order
            )

        return place_index

    def _add_item(
            self,
            trip_day: TripDay,
            place_data: Dict,
            start_time: time,
            duration_hours: float,
            item_type: str,
            sort_order: int
    ) -> time:
        """
        Add a TripItem to a TripDay

        Returns:
            End time of this item (for next item's start)
        """
        # Calculate end time
        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = start_dt + timedelta(hours=duration_hours)
        end_time = end_dt.time()

        # Calculate duration in minutes
        duration_minutes = int(duration_hours * 60)

        # Create TripItem
        TripItem.objects.create(
            day=trip_day,
            item_type=item_type,
            place_ref_id=place_data['id'],
            title=place_data['title'],
            category=place_data.get('category', ''),
            address_summary=place_data.get('address', ''),
            lat=place_data.get('lat'),
            lng=place_data.get('lng'),
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            sort_order=sort_order,
            price_tier=place_data.get('price_tier', 'FREE'),
            estimated_cost=Decimal(str(place_data.get('entry_fee', 0))),
            main_image_url=place_data.get('images', [''])[0] if place_data.get('images') else ''
        )

        return end_time

    def _find_place(
            self,
            places: List[Dict],
            category: Optional[str] = None,
            exclude_category: Optional[str] = None,
            place_index: int = 0,
            used_ids: set = None
    ) -> Optional[Dict]:
        """
        Find a suitable place from the list

        Args:
            places: List of available places
            category: Specific category to find
            exclude_category: Category to exclude
            place_index: Starting index in places list
            used_ids: Set of place IDs already used (Bug 12 fix)

        Returns:
            Place dictionary or None
        """
        if not places:
            return None

        # Filter by category
        if category:
            filtered = [p for p in places if p.get('category') == category]
        elif exclude_category:
            filtered = [p for p in places if p.get('category') != exclude_category]
        else:
            filtered = places

        # Bug 12 fix: exclude already used places
        if used_ids:
            not_used = [p for p in filtered if p.get('id') not in used_ids]
            if not_used:
                filtered = not_used
            # If all are used, allow reuse (better than returning None)

        if not filtered:
            return None

        if place_index < len(filtered):
            return filtered[place_index % len(filtered)]
        return filtered[0]

    def _calculate_trip_cost(self, trip: Trip):
        """Calculate total cost for the trip"""
        total = Decimal('0.00')

        for day in trip.days.all():
            for item in day.items.all():
                total += item.estimated_cost

        trip.total_estimated_cost = total
        trip.save(update_fields=['total_estimated_cost'])
