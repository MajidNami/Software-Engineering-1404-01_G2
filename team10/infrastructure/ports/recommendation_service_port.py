from abc import ABC, abstractmethod
from typing import List

from ...domain.enums.season import Season
from ..models.recommended_place import RecommendedPlace


class RecommendationServicePort(ABC):
    """Port for recommendation service."""

    @abstractmethod
    def get_recommendations(
        self,
        user_id: str,
        region_id: str,
        destination: str,
        season: Season
    ) -> List[RecommendedPlace]:
        """Get recommended places for a trip.

        Args:
            user_id: Hash string ID of the user.
            region_id: The region ID from facilities service.
            destination: The destination name.
            season: The season of travel.

        Returns:
            List of recommended places with place_id and score.
        """
        pass
