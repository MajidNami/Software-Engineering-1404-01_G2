from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class DailyPlanDto:
    """DTO for daily plan."""

    id: Optional[int]
    start_at: datetime
    end_at: datetime
    facility_id: int
    cost: float
    activity_type: str
    description: str
    place_source_type: str


@dataclass
class HotelScheduleDto:
    """DTO for hotel schedule."""

    id: Optional[int]
    hotel_id: int
    start_at: datetime
    end_at: datetime
    rooms_count: int
    cost: float


@dataclass
class TripDto:
    """DTO for trip response."""

    id: Optional[int]
    user_id: int
    requirements_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    daily_plans: List[DailyPlanDto]
    hotel_schedules: List[HotelScheduleDto]
    total_cost: float
