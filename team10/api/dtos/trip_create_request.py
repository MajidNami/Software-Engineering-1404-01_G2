from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class PreferenceConstraintDto:
    """DTO for preference constraint."""

    description: str
    tag: str


@dataclass
class TripCreateRequest:
    """Request DTO for creating a new trip."""

    user_id: int
    start_at: datetime
    end_at: datetime
    destination_city_id: int
    constraints: Optional[List[PreferenceConstraintDto]] = None
    budget_limit: Optional[float] = None
