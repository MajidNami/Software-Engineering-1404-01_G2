from dataclasses import dataclass
from typing import Optional


@dataclass
class Facility:
    """Represents a facility or point of interest."""

    name: str
    facility_type: str
    latitude: float
    longitude: float
    cost: float
    id: Optional[int] = None
