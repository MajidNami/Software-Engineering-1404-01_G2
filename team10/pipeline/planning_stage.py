from abc import ABC, abstractmethod

from ..application.orchestrators.trip_context import TripContext


class PlanningStage(ABC):
    """Base interface for all planning pipeline stages."""

    @abstractmethod
    def execute(self, context: TripContext) -> None:
        """Execute this stage of the planning pipeline."""
        pass
