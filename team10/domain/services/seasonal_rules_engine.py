from abc import ABC, abstractmethod
from typing import List

from ..enums.activity_type import ActivityType
from ..enums.season import Season
from ..enums.weather_condition import WeatherCondition
from ..models.weather_info import WeatherInfo
from ..models.rule_adjustment import RuleAdjustment


class SeasonalRulesEngine(ABC):
    """Interface for seasonal rules engine."""

    @abstractmethod
    def is_activity_allowed(
        self,
        activity_type: ActivityType,
        season: Season,
        weather_condition: WeatherCondition
    ) -> bool:
        """Check if an activity is allowed given the season and weather."""
        pass

    @abstractmethod
    def get_adjustments_for_current_conditions(
        self,
        season: Season,
        weather_info: WeatherInfo
    ) -> List[RuleAdjustment]:
        """Get rule adjustments based on current conditions."""
        pass
