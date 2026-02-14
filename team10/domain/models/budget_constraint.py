from dataclasses import dataclass


@dataclass
class BudgetConstraint:
    """Represents budget constraints for a trip."""

    max_budget: float
    min_budget: float
    currency: str = "USD"
