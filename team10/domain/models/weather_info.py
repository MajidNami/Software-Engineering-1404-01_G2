from dataclasses import dataclass
from ..enums.weather_condition import WeatherCondition


@dataclass
class WeatherInfo:
    """Value object representing weather information."""

    condition: WeatherCondition
    temperature: float
    humidity: float
    wind_speed: float
