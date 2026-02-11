from abc import ABC, abstractmethod

from ..entities.trip import Trip
from ..models.cost_analysis_result import CostAnalysisResult


class BudgetValidator(ABC):
    """Interface for budget validation service."""

    @abstractmethod
    def validate_budget(self, trip: Trip, budget_limit: float) -> CostAnalysisResult:
        """Validate trip budget against a limit."""
        pass
