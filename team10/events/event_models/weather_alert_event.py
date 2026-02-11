from dataclasses import dataclass


@dataclass
class WeatherAlertEvent:
    """Event triggered when there's a weather alert."""

    alert_type: str
    location: str
    severity: str
    message: str
