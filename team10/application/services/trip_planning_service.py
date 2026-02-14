from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from datetime import date

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
    def view_trip(self, trip_id: int, user_id: int) -> Tuple[Trip, str]:
        """View trip details."""
        pass

    @abstractmethod
    def analyze_costs_and_budget(self, trip_id: int, budget_limit: float) -> CostAnalysisResult:
        """Analyze trip costs against a budget."""
        pass

    @abstractmethod
    def get_user_trips(
        self,
        user_id: str,
        status: Optional[str] = None,
        destination: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        search_query: Optional[str] = None,
        sort_by: str = 'newest'
    ) -> List:
        """Get all trips for a user with optional filtering and sorting.
        
        Args:
            user_id: The user's ID
            status: Filter by status (DRAFT, IN_PROGRESS, CONFIRMED, CANCELLED, EXPIRED)
            destination: Filter by destination name (partial match)
            date_from: Filter trips starting on or after this date
            date_to: Filter trips starting on or before this date
            search_query: Search in destination name or trip ID
            sort_by: Sort order ('newest', 'oldest', 'cost')
            
        Returns:
            List of trip dictionaries with computed fields
        """
        pass
