from abc import ABC, abstractmethod
from typing import List

from ...domain.enums.season import Season
from ..models.recommended_item import RecommendedItem


class RecommendationServicePort(ABC):
    """Port for recommendation service."""

    @abstractmethod
    def get_personalized_recommendations(
        self,
        user_id: int,
        destination: str,
        season: Season
    ) -> List[RecommendedItem]:
        """Get personalized recommendations for a user."""
        pass
