from dataclasses import dataclass, field
from typing import Optional, Dict


@dataclass
class Facility:
    """Represents a facility or point of interest."""

    name: str
    facility_type: str  # HOTEL, RESTAURANT, ATTRACTION, PARK, MUSEUM, etc.
    latitude: float
    longitude: float
    cost: float  # Cost per visit/night in Rials
    id: Optional[int] = None
    region_id: Optional[str] = None
    description: Optional[str] = None
    visit_duration_minutes: int = 60  # How long a typical visit takes
    opening_hour: int = 8  # Opening hour (0-23)
    closing_hour: int = 22  # Closing hour (0-23)
    tags: list = field(default_factory=list)  # Tags like 'nature', 'history', 'food'
    rating: float = 3.0  # Rating out of 5
    
    def is_open_at(self, hour: int) -> bool:
        """Check if facility is open at given hour."""
        if self.opening_hour <= self.closing_hour:
            return self.opening_hour <= hour < self.closing_hour
        else:  # Crosses midnight
            return hour >= self.opening_hour or hour < self.closing_hour
