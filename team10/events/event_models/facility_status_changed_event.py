from dataclasses import dataclass


@dataclass
class FacilityStatusChangedEvent:
    """Event triggered when a facility status changes."""

    facility_id: int
    status: str
    change_reason: str
