from datetime import datetime
from typing import Set, Optional
from dataclasses import dataclass, field


@dataclass
class PreferenceConstraint:
    """Represents a user preference or constraint for trip planning."""

    description: str
    tag: str
    id: Optional[int] = None


@dataclass
class TripRequirements:
    """Represents user requirements for creating a trip."""

    user_id: int
    start_at: datetime
    end_at: datetime
    destination_city_id: int
    id: Optional[int] = None
    constraints: Set[PreferenceConstraint] = field(default_factory=set)

    def add_constraint(self, constraint: PreferenceConstraint) -> None:
        """Add a preference constraint to the requirements."""
        self.constraints.add(constraint)

    def get_duration_days(self) -> int:
        """Calculate the duration of the trip in days."""
        return (self.end_at - self.start_at).days + 1
