from .planning_stage import PlanningStage
from ..application.orchestrators.trip_context import TripContext


class SeasonalWeatherFilterStage(PlanningStage):
    """Stage for filtering activities based on season and weather."""

    def execute(self, context: TripContext) -> None:
        """Filter activities that are not suitable for current season/weather."""
        # Implementation will:
        # - Check weather forecasts
        # - Apply seasonal rules
        # - Filter incompatible activities
        pass
