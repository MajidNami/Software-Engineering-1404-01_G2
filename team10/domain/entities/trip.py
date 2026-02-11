from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from ..enums.trip_status import TripStatus


@dataclass
class DailyPlan:
    """Represents a single activity in a daily plan."""

    start_at: datetime
    end_at: datetime
    facility_id: int
    cost: float
    activity_type: str
    description: str
    place_source_type: str
    id: Optional[int] = None
    trip_id: Optional[int] = None


@dataclass
class HotelSchedule:
    """Represents a hotel booking within a trip."""

    hotel_id: int
    start_at: datetime
    end_at: datetime
    rooms_count: int
    cost: float
    id: Optional[int] = None
    trip_id: Optional[int] = None


@dataclass
class Trip:
    """Main Trip entity representing a complete trip plan."""

    user_id: int
    requirements_id: int
    status: TripStatus
    created_at: datetime
    updated_at: datetime
    id: Optional[int] = None
    daily_plans: List[DailyPlan] = field(default_factory=list)
    hotel_schedules: List[HotelSchedule] = field(default_factory=list)

    def add_daily_plan(self, daily_plan: DailyPlan) -> None:
        """Add a daily plan to the trip."""
        self.daily_plans.append(daily_plan)

    def add_hotel_schedule(self, hotel_schedule: HotelSchedule) -> None:
        """Add a hotel schedule to the trip."""
        self.hotel_schedules.append(hotel_schedule)

    def calculate_total_cost(self) -> float:
        """Calculate the total cost of the trip."""
        daily_plans_cost = sum(plan.cost for plan in self.daily_plans)
        hotel_cost = sum(schedule.cost for schedule in self.hotel_schedules)
        return daily_plans_cost + hotel_cost
