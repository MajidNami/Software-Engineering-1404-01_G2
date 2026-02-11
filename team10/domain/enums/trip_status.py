from enum import Enum


class TripStatus(Enum):
    """Enumeration for trip status."""

    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    NEEDS_REGENERATION = "NEEDS_REGENERATION"
