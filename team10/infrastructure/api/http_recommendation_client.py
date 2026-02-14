"""
HTTP implementation of RecommendationServicePort calling Team 12 Recommendation API.
Uses team12.yaml: GET /regions/{region_id}/places (suggestPlacesInRegion).
Optional: POST /places/score (scoreCandidatePlaces), GET /regions (suggestRegions).
"""
import logging
from typing import List

import requests

from ..ports.recommendation_service_port import RecommendationServicePort
from ..models.recommended_place import RecommendedPlace
from ...domain.enums.season import Season

logger = logging.getLogger(__name__)


class HttpRecommendationClient(RecommendationServicePort):
    """
    HTTP implementation for the Recommendation Service (Team 12).
    Base URL should point to the server (e.g. http://localhost:8000); paths use /team12/recommend/...
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 10,
        default_travel_style: str = "FAMILY",
        default_budget_level: str = "MODERATE",
        default_trip_duration_days: int = 3,
        limit_places: int = 50,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_travel_style = default_travel_style
        self.default_budget_level = default_budget_level
        self.default_trip_duration_days = default_trip_duration_days
        self.limit_places = min(50, max(1, limit_places))
        self._session = requests.Session()

    def get_recommendations(
        self,
        user_id: str,
        region_id: str,
        destination: str,
        season: Season,
    ) -> List[RecommendedPlace]:
        """
        Get recommended places for a region. Calls GET /team12/recommend/regions/{region_id}/places
        with season, budget_level, travel_style, trip_duration_days, limit.
        """
        path = f"/team12/recommend/regions/{region_id}/places"
        params = {
            "travel_style": self.default_travel_style,
            "budget_level": self.default_budget_level,
            "season": season.value,
            "trip_duration_days": self.default_trip_duration_days,
            "limit": self.limit_places,
        }
        url = f"{self.base_url}{path}"
        try:
            r = self._session.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as e:
            logger.warning("Recommendation API GET %s failed: %s", path, e)
            return []

        scored = data.get("scored_places") or []
        out = []
        for item in scored:
            if not isinstance(item, dict):
                continue
            place_id = item.get("place_id")
            score = item.get("score")
            if place_id is None:
                continue
            try:
                score_f = float(score) if score is not None else 0.5
            except (TypeError, ValueError):
                score_f = 0.5
            out.append(RecommendedPlace(place_id=str(place_id), score=score_f))
        return out
