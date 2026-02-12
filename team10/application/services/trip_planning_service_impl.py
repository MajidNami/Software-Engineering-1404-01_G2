from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from dataclasses import dataclass

from ...models import Trip as TripModel, TripRequirements as TripRequirementsModel, PreferenceConstraint as PreferenceConstraintModel
from ...domain.entities.trip import Trip
from ...domain.models.change_trigger import ChangeTrigger
from ...domain.models.cost_analysis_result import CostAnalysisResult
from ...domain.models.facility import Facility
from ...domain.services.season_calculator import calculate_season_iran
from ...infrastructure.ports.facilities_service_port import FacilitiesServicePort
from ...infrastructure.ports.recommendation_service_port import RecommendationServicePort
from ...infrastructure.models.recommended_place import RecommendedPlace
from .trip_planning_service import TripPlanningService


@dataclass
class DayScheduleSlot:
    """Represents a time slot in a day's schedule."""
    start_hour: int
    start_minute: int
    end_hour: int
    end_minute: int
    slot_type: str  # 'BREAKFAST', 'ACTIVITY', 'LUNCH', 'DINNER', 'RETURN_HOTEL'
    facility: Optional[Facility] = None
    description: str = ""


class TripPlanningServiceImpl(TripPlanningService):
    """Concrete implementation of TripPlanningService using Django ORM."""

    # Budget level thresholds (cost per night in Rials)
    BUDGET_THRESHOLDS = {
        'HOTEL': {
            'ECONOMY': (0, 4000000),       # 0 - 4M Rials
            'MODERATE': (4000000, 10000000),  # 4M - 10M Rials
            'LUXURY': (10000000, float('inf'))  # 10M+ Rials
        },
        'RESTAURANT': {
            'ECONOMY': (0, 500000),        # 0 - 500k Rials
            'MODERATE': (500000, 1000000),  # 500k - 1M Rials
            'LUXURY': (1000000, float('inf'))  # 1M+ Rials
        }
    }

    # Day schedule timing constants
    BREAKFAST_START = 7
    BREAKFAST_END = 8
    MORNING_ACTIVITY_START = 9
    LUNCH_START = 12
    LUNCH_END = 14
    AFTERNOON_ACTIVITY_START = 14
    DINNER_START = 19
    DINNER_END = 21
    LATEST_RETURN = 23  # Latest time user can stay out

    def __init__(
        self,
        facilities_service: FacilitiesServicePort,
        recommendation_service: RecommendationServicePort
    ):
        self._facilities_service = facilities_service
        self._recommendation_service = recommendation_service

    def create_initial_trip(self, requirements_data: dict, user_id: str) -> TripModel:
        """Create an initial trip based on user requirements.

        Args:
            requirements_data: Dictionary containing trip requirements
            user_id: Hash string ID of the user from central auth system
        """
        # Parse dates
        start_date = datetime.fromisoformat(requirements_data['start_date'])
        end_date = datetime.fromisoformat(requirements_data['end_date'])

        # Search region via facilities service
        destination_query = requirements_data['destination']
        region = self._facilities_service.search_region(destination_query)
        if region is None:
            raise ValueError(f"Region not found for destination: {destination_query}")

        # Calculate season based on start date (Iran calendar)
        season = calculate_season_iran(start_date)

        # Get recommended places from recommender service
        recommended_places = self._recommendation_service.get_recommendations(
            user_id=user_id,
            region_id=region.id,
            destination=region.name,
            season=season
        )

        budget_level = requirements_data.get('budget_level', 'MODERATE')
        preferences = requirements_data.get('preferences', [])

        # Create TripRequirements
        requirements = TripRequirementsModel.objects.create(
            user_id=user_id,
            start_at=start_date,
            end_at=end_date,
            destination_name=region.name,
            region_id=region.id,
            budget_level=budget_level,
            travelers_count=requirements_data.get('travelers_count', 1)
        )

        # Create preference constraints
        for pref in preferences:
            PreferenceConstraintModel.objects.create(
                requirements=requirements,
                description=self._get_preference_description(pref),
                tag=pref
            )

        # Create Trip
        trip = TripModel.objects.create(
            user_id=user_id,
            requirements=requirements,
            destination_name=region.name,
            status='DRAFT'
        )

        # Build the actual daily plan using recommendations
        self._create_trip_plan(
            trip=trip,
            start_date=start_date,
            end_date=end_date,
            region_id=region.id,
            budget_level=budget_level,
            preferences=preferences,
            recommended_places=recommended_places
        )

        print(f"[TripPlanning] Region: {region.name} (id={region.id})")
        print(f"[TripPlanning] Season: {season.value}")
        print(f"[TripPlanning] Recommended places: {[(p.place_id, p.score) for p in recommended_places]}")

        return trip

    def _create_trip_plan(
        self,
        trip: TripModel,
        start_date: datetime,
        end_date: datetime,
        region_id: str,
        budget_level: str,
        preferences: List[str],
        recommended_places: List[RecommendedPlace]
    ):
        """Create a complete trip plan with hotel, restaurants, and activities.
        
        Args:
            trip: The trip model to add plans to
            start_date: Trip start date
            end_date: Trip end date
            region_id: The region ID
            budget_level: Budget level (ECONOMY, MODERATE, LUXURY)
            preferences: List of preference tags
            recommended_places: List of recommended places from recommendation service
        """
        from ...models import DailyPlan, HotelSchedule

        # 1. Select a hotel based on budget level
        hotel = self._select_hotel(region_id, budget_level)
        if hotel is None:
            raise ValueError(f"No hotel found in region {region_id}")

        # Calculate number of nights
        duration_days = (end_date - start_date).days
        
        # Create hotel schedule
        HotelSchedule.objects.create(
            trip=trip,
            hotel_id=hotel.id,
            start_at=start_date,
            end_at=end_date,
            rooms_count=1,
            cost=hotel.cost * duration_days
        )

        # 2. Get restaurants in region
        restaurants = self._facilities_service.get_restaurants_in_region(region_id)
        
        # 3. Convert recommended places to facilities and sort by score
        attractions = self._get_attractions_from_recommendations(
            recommended_places, region_id, preferences
        )
        
        # Track visited places to avoid duplicates
        visited_place_ids = set()
        attraction_index = 0

        # 4. Plan each day
        current_date = start_date
        while current_date < end_date:
            # Track current time and location
            current_time = current_date.replace(hour=self.BREAKFAST_START, minute=0)
            current_facility = hotel

            # Morning: Start from hotel with breakfast (at hotel)
            DailyPlan.objects.create(
                trip=trip,
                facility_id=hotel.id,
                start_at=current_date.replace(hour=self.BREAKFAST_START, minute=0),
                end_at=current_date.replace(hour=self.BREAKFAST_END, minute=0),
                activity_type='FOOD',
                description=f"صبحانه در {hotel.name}",
                place_source_type='FACILITIES',
                cost=0  # Included in hotel
            )
            current_time = current_date.replace(hour=self.BREAKFAST_END, minute=0)

            # Morning activity (9:00 - 12:00)
            morning_activity, attraction_index, visited_place_ids = self._plan_activity_slot(
                trip=trip,
                current_date=current_date,
                start_hour=self.MORNING_ACTIVITY_START,
                end_hour=self.LUNCH_START,
                attractions=attractions,
                attraction_index=attraction_index,
                visited_place_ids=visited_place_ids,
                current_facility=current_facility,
                preferences=preferences,
                is_golden_hour=True  # Morning is golden hour for high-priority activities
            )
            
            if morning_activity:
                current_facility = morning_activity

            # Lunch (12:30 - 14:00)
            lunch_restaurant = self._select_restaurant_near_facility(
                restaurants, current_facility, budget_level
            )
            if lunch_restaurant:
                # Calculate travel time to restaurant
                travel_info = self._facilities_service.get_travel_info(
                    current_facility.id, lunch_restaurant.id
                )
                lunch_start = current_date.replace(hour=12, minute=30)
                
                DailyPlan.objects.create(
                    trip=trip,
                    facility_id=lunch_restaurant.id,
                    start_at=lunch_start,
                    end_at=current_date.replace(hour=14, minute=0),
                    activity_type='FOOD',
                    description=f"ناهار در {lunch_restaurant.name}",
                    place_source_type='FACILITIES',
                    cost=lunch_restaurant.cost
                )
                current_facility = lunch_restaurant
            else:
                # Fallback: eat at hotel
                DailyPlan.objects.create(
                    trip=trip,
                    facility_id=hotel.id,
                    start_at=current_date.replace(hour=12, minute=30),
                    end_at=current_date.replace(hour=14, minute=0),
                    activity_type='FOOD',
                    description=f"ناهار در {hotel.name}",
                    place_source_type='FACILITIES',
                    cost=500000  # Estimate for hotel lunch
                )
                current_facility = hotel

            # Afternoon activity (14:30 - 18:00)
            afternoon_activity, attraction_index, visited_place_ids = self._plan_activity_slot(
                trip=trip,
                current_date=current_date,
                start_hour=14,
                end_hour=18,
                attractions=attractions,
                attraction_index=attraction_index,
                visited_place_ids=visited_place_ids,
                current_facility=current_facility,
                preferences=preferences,
                is_golden_hour=False
            )
            
            if afternoon_activity:
                current_facility = afternoon_activity

            # Dinner (19:00 - 20:30)
            dinner_restaurant = self._select_restaurant_near_facility(
                restaurants, current_facility, budget_level
            )
            if dinner_restaurant and dinner_restaurant.id != (lunch_restaurant.id if lunch_restaurant else None):
                DailyPlan.objects.create(
                    trip=trip,
                    facility_id=dinner_restaurant.id,
                    start_at=current_date.replace(hour=19, minute=0),
                    end_at=current_date.replace(hour=20, minute=30),
                    activity_type='FOOD',
                    description=f"شام در {dinner_restaurant.name}",
                    place_source_type='FACILITIES',
                    cost=dinner_restaurant.cost
                )
                current_facility = dinner_restaurant
            else:
                # Fallback: eat at hotel
                DailyPlan.objects.create(
                    trip=trip,
                    facility_id=hotel.id,
                    start_at=current_date.replace(hour=19, minute=0),
                    end_at=current_date.replace(hour=20, minute=30),
                    activity_type='FOOD',
                    description=f"شام در {hotel.name}",
                    place_source_type='FACILITIES',
                    cost=700000  # Estimate for hotel dinner
                )
                current_facility = hotel

            # Optional evening activity if there's time and attractions left
            if attraction_index < len(attractions):
                # Check if there's an evening attraction open until late
                evening_activity, attraction_index, visited_place_ids = self._plan_activity_slot(
                    trip=trip,
                    current_date=current_date,
                    start_hour=21,
                    end_hour=23,
                    attractions=attractions,
                    attraction_index=attraction_index,
                    visited_place_ids=visited_place_ids,
                    current_facility=current_facility,
                    preferences=preferences,
                    is_golden_hour=False,
                    is_optional=True
                )
                if evening_activity:
                    current_facility = evening_activity

            current_date += timedelta(days=1)

    def _select_hotel(self, region_id: str, budget_level: str) -> Optional[Facility]:
        """Select the first hotel that matches the budget level.
        
        Args:
            region_id: The region to search in
            budget_level: The budget level (ECONOMY, MODERATE, LUXURY)
            
        Returns:
            The first matching hotel or None
        """
        hotels = self._facilities_service.get_hotels_in_region(region_id)
        
        # Find first hotel matching budget level
        for hotel in hotels:
            if self._cost_to_budget_level(hotel.cost, 'HOTEL') == budget_level:
                return hotel
        
        # Fallback: return any hotel if no exact match
        if hotels:
            return hotels[0]
        
        return None

    def _cost_to_budget_level(self, cost: float, facility_type: str) -> str:
        """Convert a facility cost to budget level.
        
        Args:
            cost: The cost of the facility
            facility_type: The type of facility ('HOTEL', 'RESTAURANT')
            
        Returns:
            Budget level string: 'ECONOMY', 'MODERATE', or 'LUXURY'
        """
        thresholds = self.BUDGET_THRESHOLDS.get(facility_type, self.BUDGET_THRESHOLDS['HOTEL'])
        
        for level, (min_cost, max_cost) in thresholds.items():
            if min_cost <= cost < max_cost:
                return level
        
        return 'MODERATE'  # Default fallback

    def _get_attractions_from_recommendations(
        self,
        recommended_places: List[RecommendedPlace],
        region_id: str,
        preferences: List[str]
    ) -> List[Tuple[Facility, float]]:
        """Convert recommended places to facilities and sort by score and preference match.
        
        Args:
            recommended_places: List of recommended places from recommendation service
            region_id: The region ID
            preferences: List of user preference tags
            
        Returns:
            List of (Facility, adjusted_score) tuples sorted by score descending
        """
        attractions = []
        
        for rec in recommended_places:
            facility = self._facilities_service.get_facility_by_place_id(rec.place_id, region_id)
            if facility:
                # Adjust score based on preference match
                adjusted_score = rec.score
                for tag in facility.tags:
                    if tag in preferences:
                        adjusted_score += 0.2  # Boost for matching preferences
                attractions.append((facility, adjusted_score))
        
        # Sort by adjusted score descending (highest priority first)
        attractions.sort(key=lambda x: x[1], reverse=True)
        
        return attractions

    def _plan_activity_slot(
        self,
        trip: TripModel,
        current_date: datetime,
        start_hour: int,
        end_hour: int,
        attractions: List[Tuple[Facility, float]],
        attraction_index: int,
        visited_place_ids: set,
        current_facility: Facility,
        preferences: List[str],
        is_golden_hour: bool = False,
        is_optional: bool = False
    ) -> Tuple[Optional[Facility], int, set]:
        """Plan an activity for a time slot.
        
        Args:
            trip: The trip model
            current_date: The current day
            start_hour: Slot start hour
            end_hour: Slot end hour
            attractions: List of (Facility, score) tuples
            attraction_index: Current index in attractions list
            visited_place_ids: Set of already visited place IDs
            current_facility: Current location facility
            preferences: User preference tags
            is_golden_hour: If True, prefer high-scored attractions
            is_optional: If True, skip if no suitable attraction
            
        Returns:
            Tuple of (selected facility or None, new attraction index, updated visited set)
        """
        from ...models import DailyPlan

        # Find next unvisited attraction that's open during this slot
        selected_attraction = None
        
        for i in range(attraction_index, len(attractions)):
            facility, score = attractions[i]
            
            # Skip if already visited
            if facility.id in visited_place_ids:
                continue
            
            # Check if facility is open during this time slot
            if not facility.is_open_at(start_hour):
                continue
            
            # For golden hour, prefer attractions matching top preferences
            if is_golden_hour and preferences:
                # Check if this attraction matches the highest priority preference
                matches_top_preference = any(tag in preferences[:2] for tag in facility.tags)
                if matches_top_preference:
                    selected_attraction = facility
                    attraction_index = i + 1
                    break
            
            # Otherwise take the next available attraction
            selected_attraction = facility
            attraction_index = i + 1
            break

        if selected_attraction is None:
            if is_optional:
                return None, attraction_index, visited_place_ids
            # No suitable attraction found for mandatory slot
            return None, attraction_index, visited_place_ids

        # Calculate travel time from current location
        travel_info = self._facilities_service.get_travel_info(
            current_facility.id, selected_attraction.id
        )
        
        # Adjust start time to account for travel
        actual_start = current_date.replace(hour=start_hour, minute=0) + timedelta(minutes=travel_info.duration_minutes)
        
        # Calculate activity duration (use facility's visit duration or time until slot end)
        visit_duration = min(
            selected_attraction.visit_duration_minutes,
            (end_hour - actual_start.hour) * 60 - actual_start.minute
        )
        
        actual_end = actual_start + timedelta(minutes=visit_duration)
        
        # Don't exceed slot end time
        slot_end = current_date.replace(hour=end_hour, minute=0)
        if actual_end > slot_end:
            actual_end = slot_end

        # Determine activity type based on facility tags
        activity_type = self._determine_activity_type(selected_attraction.tags, preferences)

        # Create the daily plan entry
        DailyPlan.objects.create(
            trip=trip,
            facility_id=selected_attraction.id,
            start_at=actual_start,
            end_at=actual_end,
            activity_type=activity_type,
            description=f"بازدید از {selected_attraction.name}",
            place_source_type='RECOMMENDATION',
            cost=selected_attraction.cost
        )

        # Mark as visited
        visited_place_ids.add(selected_attraction.id)

        return selected_attraction, attraction_index, visited_place_ids

    def _select_restaurant_near_facility(
        self,
        restaurants: List[Facility],
        current_facility: Facility,
        budget_level: str
    ) -> Optional[Facility]:
        """Select a restaurant near the current facility matching budget.
        
        Priority:
        1. Close to current location AND matches budget
        2. Any restaurant matching budget
        3. Any restaurant
        
        Args:
            restaurants: List of available restaurants
            current_facility: Current location
            budget_level: Target budget level
            
        Returns:
            Selected restaurant or None
        """
        if not restaurants:
            return None

        # Calculate distances and filter by budget
        restaurant_distances = []
        for restaurant in restaurants:
            travel_info = self._facilities_service.get_travel_info(
                current_facility.id, restaurant.id
            )
            matches_budget = self._cost_to_budget_level(restaurant.cost, 'RESTAURANT') == budget_level
            restaurant_distances.append((restaurant, travel_info.distance_km, matches_budget))

        # Sort by: budget match first, then distance
        restaurant_distances.sort(key=lambda x: (not x[2], x[1]))

        if restaurant_distances:
            return restaurant_distances[0][0]
        
        return None

    def _determine_activity_type(self, tags: List[str], preferences: List[str]) -> str:
        """Determine the activity type based on facility tags.
        
        Args:
            tags: Facility tags
            preferences: User preferences
            
        Returns:
            Activity type string
        """
        tag_to_activity = {
            'nature': 'OUTDOOR',
            'history': 'CULTURE',
            'culture': 'CULTURE',
            'shopping': 'SHOPPING',
            'food': 'FOOD',
            'relax': 'RELAX',
            'adventure': 'OUTDOOR',
            'nightlife': 'NIGHTLIFE',
            'modern': 'SIGHTSEEING',
            'religion': 'CULTURE',
        }
        
        # First check if any tag matches user preferences
        for pref in preferences:
            if pref in tags:
                return tag_to_activity.get(pref, 'SIGHTSEEING')
        
        # Otherwise use first matching tag
        for tag in tags:
            if tag in tag_to_activity:
                return tag_to_activity[tag]
        
        return 'SIGHTSEEING'

    def regenerate_by_styles(self, trip_id: int, styles: List[str]) -> Trip:
        """Regenerate a trip with different styles/preferences."""
        trip = TripModel.objects.get(id=trip_id)

        # Clear existing plans
        trip.daily_plans.all().delete()
        trip.hotel_schedules.all().delete()

        # Update preferences
        trip.requirements.constraints.all().delete()
        for style in styles:
            PreferenceConstraintModel.objects.create(
                requirements=trip.requirements,
                description=self._get_preference_description(style),
                tag=style
            )

        # Get region and recommendations for regeneration
        region_id = trip.requirements.region_id
        season = calculate_season_iran(trip.requirements.start_at)
        
        recommended_places = self._recommendation_service.get_recommendations(
            user_id=trip.user_id,
            region_id=region_id,
            destination=trip.requirements.destination_name,
            season=season
        )

        # Regenerate plan with new styles
        self._create_trip_plan(
            trip=trip,
            start_date=trip.requirements.start_at,
            end_date=trip.requirements.end_at,
            region_id=region_id,
            budget_level=trip.requirements.budget_level,
            preferences=styles,
            recommended_places=recommended_places
        )

        trip.updated_at = datetime.now()
        trip.save()

        return trip

    def replan_due_to_changes(self, trip_id: int, change_trigger: ChangeTrigger) -> Trip:
        """Replan a trip due to external changes."""
        trip = TripModel.objects.get(id=trip_id)
        trip.status = 'NEEDS_REGENERATION'
        trip.save()

        # TODO: Implement replanning logic based on change trigger

        return trip

    def view_trip(self, trip_id: int, user_id: str) -> TripModel:
        """View trip details."""
        trip = TripModel.objects.get(id=trip_id, user_id=user_id)
        return trip

    def analyze_costs_and_budget(self, trip_id: int, budget_limit: float) -> CostAnalysisResult:
        """Analyze trip costs against a budget."""
        trip = TripModel.objects.get(id=trip_id)
        total_cost = float(trip.calculate_total_cost())

        is_within_budget = total_cost <= budget_limit
        percentage = (total_cost / budget_limit * 100) if budget_limit > 0 else 0

        if is_within_budget:
            analysis = f"Trip cost is within budget. Using {percentage:.1f}% of budget."
        else:
            over_amount = total_cost - budget_limit
            analysis = f"Trip exceeds budget by {over_amount:.2f}. Consider reducing activities or accommodation."

        return CostAnalysisResult(
            total_cost=total_cost,
            budget_limit=budget_limit,
            is_within_budget=is_within_budget,
            analysis=analysis
        )

    def _get_preference_description(self, preference_tag: str) -> str:
        """Get description for preference tag."""
        descriptions = {
            'nature': 'Interested in nature and outdoor activities',
            'history': 'Interested in historical and cultural sites',
            'food': 'Interested in local cuisine and restaurants',
            'relax': 'Prefers relaxation and leisure activities',
            'adventure': 'Seeks adventurous and thrilling experiences',
            'shopping': 'Enjoys shopping and markets',
            'nightlife': 'Interested in nighttime entertainment'
        }
        return descriptions.get(preference_tag, f'Preference: {preference_tag}')
