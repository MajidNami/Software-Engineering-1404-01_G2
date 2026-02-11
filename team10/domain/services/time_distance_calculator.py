from abc import ABC, abstractmethod
from datetime import timedelta

from ..models.facility import Facility
from ..enums.transport_mode import TransportMode


class TimeDistanceCalculator(ABC):
    """Interface for calculating time and distance between facilities."""

    @abstractmethod
    def calculate_travel_time_between(
        self,
        from_facility: Facility,
        to_facility: Facility,
        transport_mode: TransportMode
    ) -> timedelta:
        """Calculate travel time between two facilities."""
        pass

    @abstractmethod
    def estimate_distance_km(
        self,
        from_facility: Facility,
        to_facility: Facility
    ) -> float:
        """Estimate distance in kilometers between two facilities."""
        pass
