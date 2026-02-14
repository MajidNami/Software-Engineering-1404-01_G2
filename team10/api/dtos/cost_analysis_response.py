from dataclasses import dataclass


@dataclass
class CostAnalysisResponse:
    """Response DTO for cost analysis."""

    total_cost: float
    budget_limit: float
    is_within_budget: bool
    analysis: str
    percentage_of_budget: float
