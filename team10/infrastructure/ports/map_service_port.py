from abc import ABC, abstractmethod
from datetime import timedelta

from ...domain.enums.transport_mode import TransportMode
from ..models.location import Location
from ..models.coordinates import Coordinates


class MapServicePort(ABC):
    """Port for map/navigation services."""

    @abstractmethod
    def get_travel_time(
        self,
        origin: Location,
        destination: Location,
        transport_mode: TransportMode
    ) -> timedelta:
        """Get travel time between two locations."""
        pass

    @abstractmethod
    def get_distance_km(self, origin: Location, destination: Location) -> float:
        """Get distance in kilometers between two locations."""
        pass

    @abstractmethod
    def get_coordinates(self, address: str) -> Coordinates:
        """Get coordinates for an address."""
        pass
