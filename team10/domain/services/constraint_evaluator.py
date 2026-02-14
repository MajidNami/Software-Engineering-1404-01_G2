from abc import ABC, abstractmethod
from typing import List

from ..entities.trip import Trip
from ..entities.trip_requirements import TripRequirements
from ..models.constraint_violation import ConstraintViolation


class ConstraintEvaluator(ABC):
    """Interface for evaluating trip constraints."""

    @abstractmethod
    def evaluate_all_constraints(
        self,
        trip: Trip,
        requirements: TripRequirements
    ) -> List[ConstraintViolation]:
        """Evaluate all constraints for a trip."""
        pass
