from dataclasses import dataclass


@dataclass
class RuleAdjustment:
    """Represents an adjustment to planning rules based on conditions."""

    description: str
    adjustment_type: str
    priority: int
