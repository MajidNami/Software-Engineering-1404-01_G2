from enum import Enum


class PlaceSourceType(Enum):
    """Enumeration for the source of a place recommendation."""

    WIKI = "WIKI"
    RECOMMENDATION = "RECOMMENDATION"
    FACILITIES = "FACILITIES"
    MANUAL = "MANUAL"
    EVENT = "EVENT"
