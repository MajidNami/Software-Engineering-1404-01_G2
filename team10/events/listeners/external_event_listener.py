from abc import ABC, abstractmethod

from ..event_models.facility_status_changed_event import FacilityStatusChangedEvent
from ..event_models.weather_alert_event import WeatherAlertEvent
from ..event_models.event_cancelled_event import EventCancelledEvent


class ExternalEventListener(ABC):
    """Listener for external events that may trigger trip replanning."""

    @abstractmethod
    def on_facility_closed(self, event: FacilityStatusChangedEvent) -> None:
        """Handle facility status change event."""
        pass

    @abstractmethod
    def on_weather_alert(self, event: WeatherAlertEvent) -> None:
        """Handle weather alert event."""
        pass

    @abstractmethod
    def on_event_cancelled(self, event: EventCancelledEvent) -> None:
        """Handle event cancellation."""
        pass
