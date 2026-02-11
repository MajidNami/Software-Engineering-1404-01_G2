from .planning_stage import PlanningStage
from ..application.orchestrators.trip_context import TripContext


class CollectDataStage(PlanningStage):
    """Stage for collecting data from various services."""

    def execute(self, context: TripContext) -> None:
        """Collect necessary data for trip planning."""
        # Implementation will gather data from:
        # - Weather service
        # - Facilities service
        # - Wiki service
        # - Recommendation service
        pass
