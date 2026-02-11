from dataclasses import dataclass
from datetime import datetime

from ...domain.models.weather_info import WeatherInfo
from ...domain.enums.weather_condition import WeatherCondition


@dataclass
class WeatherForecast:
    """Weather forecast for a specific date."""

    weather_info: WeatherInfo
    forecast_date: datetime
    condition: WeatherCondition
    temperature: float
