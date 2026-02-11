from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchCriteria:
    """Criteria for searching facilities in an area."""

    latitude: float
    longitude: float
    radius: float
    facility_type: Optional[str] = None
