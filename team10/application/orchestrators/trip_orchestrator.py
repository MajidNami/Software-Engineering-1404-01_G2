from abc import ABC, abstractmethod

from ...domain.entities.trip import Trip
from ...domain.entities.trip_requirements import TripRequirements
from ...domain.models.change_trigger import ChangeTrigger
from .trip_context import TripContext


class TripOrchestrator(ABC):
    """Orchestrates the trip planning pipeline."""

    @abstractmethod
    def orchestrate_initial_planning(self, requirements: TripRequirements) -> Trip:
        """Orchestrate the initial trip planning process."""
        pass

    @abstractmethod
    def orchestrate_replanning(self, trip: Trip, change_trigger: ChangeTrigger) -> None:
        """Orchestrate replanning of an existing trip."""
        pass

    @abstractmethod
    def execute_planning_pipeline(self, context: TripContext) -> Trip:
        """Execute the planning pipeline with given context."""
        pass
