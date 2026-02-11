from datetime import datetime, timedelta
from typing import List
from django.contrib.auth.models import User

from ...models import Trip as TripModel, TripRequirements as TripRequirementsModel, PreferenceConstraint as PreferenceConstraintModel
from ...domain.entities.trip import Trip
from ...domain.entities.trip_requirements import TripRequirements
from ...domain.models.change_trigger import ChangeTrigger
from ...domain.models.cost_analysis_result import CostAnalysisResult
from ...domain.enums.trip_status import TripStatus
from .trip_planning_service import TripPlanningService


class TripPlanningServiceImpl(TripPlanningService):
    """Concrete implementation of TripPlanningService using Django ORM."""

    def create_initial_trip(self, requirements_data: dict, user: User) -> TripModel:
        """Create an initial trip based on user requirements."""

        # Parse dates
        start_date = datetime.fromisoformat(requirements_data['start_date'])
        end_date = datetime.fromisoformat(requirements_data['end_date'])

        # Create TripRequirements
        requirements = TripRequirementsModel.objects.create(
            user=user,
            start_at=start_date,
            end_at=end_date,
            destination_name=requirements_data['destination'],
            budget=requirements_data.get('budget'),
            travelers_count=requirements_data.get('travelers_count', 1)
        )

        # Create preference constraints
        preferences = requirements_data.get('preferences', [])
        for pref in preferences:
            PreferenceConstraintModel.objects.create(
                requirements=requirements,
                description=self._get_preference_description(pref),
                tag=pref
            )

        # Create Trip
        trip = TripModel.objects.create(
            user=user,
            requirements=requirements,
            status='DRAFT'
        )

        # TODO: Execute planning pipeline to generate daily plans and hotel schedules
        # For now, create a simple placeholder plan
        self._create_placeholder_plan(trip, start_date, end_date)

        return trip

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

        # Regenerate plan
        self._create_placeholder_plan(
            trip,
            trip.requirements.start_at,
            trip.requirements.end_at
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

    def view_trip(self, trip_id: int, user_id: int) -> TripModel:
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

    def _create_placeholder_plan(self, trip: TripModel, start_date: datetime, end_date: datetime):
        """Create a placeholder plan for the trip."""
        from ...models import DailyPlan, HotelSchedule

        # Calculate number of days
        duration = (end_date - start_date).days

        # Create hotel schedule for the entire duration
        HotelSchedule.objects.create(
            trip=trip,
            hotel_id=1,  # Placeholder
            start_at=start_date,
            end_at=end_date,
            rooms_count=1,
            cost=duration * 1000000  # 1M per night placeholder
        )

        # Create daily activities
        current_date = start_date
        preferences = list(trip.requirements.constraints.values_list('tag', flat=True))

        while current_date < end_date:
            # Morning activity
            DailyPlan.objects.create(
                trip=trip,
                start_at=current_date.replace(hour=9, minute=0),
                end_at=current_date.replace(hour=12, minute=0),
                activity_type=self._map_preference_to_activity(preferences[0] if preferences else 'history'),
                description=f"Morning activity at {trip.requirements.destination_name}",
                place_source_type='RECOMMENDATION',
                cost=500000
            )

            # Afternoon activity
            DailyPlan.objects.create(
                trip=trip,
                start_at=current_date.replace(hour=14, minute=0),
                end_at=current_date.replace(hour=18, minute=0),
                activity_type='FOOD',
                description=f"Lunch and exploration in {trip.requirements.destination_name}",
                place_source_type='RECOMMENDATION',
                cost=300000
            )

            current_date += timedelta(days=1)

    def _map_preference_to_activity(self, preference: str) -> str:
        """Map preference tag to activity type."""
        mapping = {
            'nature': 'OUTDOOR',
            'history': 'CULTURE',
            'food': 'FOOD',
            'relax': 'RELAX',
            'adventure': 'OUTDOOR',
            'shopping': 'SHOPPING',
            'nightlife': 'NIGHTLIFE'
        }
        return mapping.get(preference, 'SIGHTSEEING')
