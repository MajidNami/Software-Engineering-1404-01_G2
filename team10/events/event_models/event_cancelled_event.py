from dataclasses import dataclass


@dataclass
class EventCancelledEvent:
    """Event triggered when an event is cancelled."""

    event_id: int
    reason: str
    event_name: str
