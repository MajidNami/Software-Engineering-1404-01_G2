from dataclasses import dataclass


@dataclass
class BudgetCheckRequest:
    """Request DTO for budget checking."""

    budget_limit: float
    currency: str = "USD"
