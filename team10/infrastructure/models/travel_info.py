from dataclasses import dataclass
from enum import Enum


class TransportMode(Enum):
    """Mode of transportation between facilities."""
    WALKING = "WALKING"
    DRIVING = "DRIVING"
    PUBLIC_TRANSIT = "PUBLIC_TRANSIT"
    TAXI = "TAXI"


@dataclass
class TravelInfo:
    """Information about travel between two facilities.
    
    This is returned by the Facilities service and includes
    the estimated cost of travel.
    """
    
    from_facility_id: int
    to_facility_id: int
    distance_km: float  # Distance in kilometers
    duration_minutes: int  # Estimated travel time in minutes
    transport_mode: TransportMode  # Recommended transport mode
    estimated_cost: float  # Estimated travel cost in Rials
    
    @property
    def is_walkable(self) -> bool:
        """Check if distance is walkable (under 1.5 km)."""
        return self.distance_km <= 1.5
