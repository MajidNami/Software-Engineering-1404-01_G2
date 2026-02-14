from dataclasses import dataclass


@dataclass
class CostAnalysisResult:
    """Result of budget analysis for a trip."""

    total_cost: float
    budget_limit: float
    is_within_budget: bool
    analysis: str
