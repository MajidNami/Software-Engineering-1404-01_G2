from dataclasses import dataclass
from datetime import datetime


@dataclass
class FacilityCostEstimate:
    """Cost estimate for a facility during a specific period."""

    facility_id: int
    estimated_cost: float
    period_start: datetime
    period_end: datetime
