from dataclasses import dataclass


@dataclass
class Coordinates:
    """Represents geographic coordinates."""

    latitude: float
    longitude: float
