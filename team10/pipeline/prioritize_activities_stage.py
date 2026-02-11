from .planning_stage import PlanningStage
from ..application.orchestrators.trip_context import TripContext


class PrioritizeActivitiesStage(PlanningStage):
    """Stage for prioritizing activities based on user preferences."""

    def execute(self, context: TripContext) -> None:
        """Prioritize activities based on constraints and preferences."""
        # Implementation will prioritize activities based on:
        # - User preferences
        # - Available facilities
        # - Season and weather
        pass
