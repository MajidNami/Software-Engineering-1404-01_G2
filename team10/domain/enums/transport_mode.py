from enum import Enum


class TransportMode(Enum):
    """Enumeration for transportation modes."""

    WALKING = "WALKING"
    DRIVING = "DRIVING"
    PUBLIC_TRANSPORT = "PUBLIC_TRANSPORT"
    CYCLING = "CYCLING"
    TAXI = "TAXI"
