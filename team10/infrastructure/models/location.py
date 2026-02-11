from dataclasses import dataclass


@dataclass
class Location:
    """Represents a geographic location."""

    latitude: float
    longitude: float
    address: str
