from dataclasses import dataclass, field
from typing import List, Optional

from ...domain.entities.trip import Trip
from ...domain.entities.trip_requirements import TripRequirements
from ...domain.models.weather_info import WeatherInfo
from ...domain.enums.season import Season
from ...domain.models.facility import Facility
from ...domain.models.budget_constraint import BudgetConstraint
from ...domain.models.constraint_violation import ConstraintViolation


@dataclass
class TripContext:
    """Context object containing all information needed for trip planning."""

    requirements: TripRequirements
    trip: Optional[Trip] = None
    current_weather: Optional[WeatherInfo] = None
    current_season: Optional[Season] = None
    available_facilities: List[Facility] = field(default_factory=list)
    budget_constraint: Optional[BudgetConstraint] = None
    violations: List[ConstraintViolation] = field(default_factory=list)
