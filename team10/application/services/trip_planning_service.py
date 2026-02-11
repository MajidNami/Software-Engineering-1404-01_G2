from abc import ABC, abstractmethod
from typing import List

from ...domain.entities.trip import Trip
from ...domain.entities.trip_requirements import TripRequirements
from ...domain.models.change_trigger import ChangeTrigger
from ...domain.models.cost_analysis_result import CostAnalysisResult


class TripPlanningService(ABC):
    """Application service interface for trip planning operations."""

    @abstractmethod
    def create_initial_trip(self, requirements: TripRequirements) -> Trip:
        """Create an initial trip based on user requirements."""
        pass

    @abstractmethod
    def regenerate_by_styles(self, trip_id: int, styles: List[str]) -> Trip:
        """Regenerate a trip with different styles/preferences."""
        pass

    @abstractmethod
    def replan_due_to_changes(self, trip_id: int, change_trigger: ChangeTrigger) -> Trip:
        """Replan a trip due to external changes."""
        pass

    @abstractmethod
    def view_trip(self, trip_id: int, user_id: int) -> Trip:
        """View trip details."""
        pass

    @abstractmethod
    def analyze_costs_and_budget(self, trip_id: int, budget_limit: float) -> CostAnalysisResult:
        """Analyze trip costs against a budget."""
        pass
