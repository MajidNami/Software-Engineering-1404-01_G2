from abc import ABC, abstractmethod
from datetime import datetime

from ...domain.enums.season import Season
from ..models.coordinates import Coordinates
from ..models.weather_forecast import WeatherForecast


class WeatherServicePort(ABC):
    """Port for weather service."""

    @abstractmethod
    def get_forecast(
        self,
        coordinates: Coordinates,
        start_date: datetime,
        end_date: datetime
    ) -> WeatherForecast:
        """Get weather forecast for a location and time period."""
        pass

    @abstractmethod
    def detect_season(self, date: datetime, coordinates: Coordinates) -> Season:
        """Detect the season for a given date and location."""
        pass
