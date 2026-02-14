from enum import Enum


class ActivityType(Enum):
    """Enumeration for different types of activities in a trip."""

    SIGHTSEEING = "SIGHTSEEING"
    FOOD = "FOOD"
    SHOPPING = "SHOPPING"
    OUTDOOR = "OUTDOOR"
    CULTURE = "CULTURE"
    RELAX = "RELAX"
    NIGHTLIFE = "NIGHTLIFE"
    TRANSPORT = "TRANSPORT"
    OTHER = "OTHER"
