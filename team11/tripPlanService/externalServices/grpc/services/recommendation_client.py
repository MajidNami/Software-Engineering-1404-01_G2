"""
Recommendation Service Client
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class RecommendationClient:
    """
    Client for ranking and recommending places based on user interests
    """

    def __init__(self):
        logger.info("RecommendationClient initialized")

    def rank_places(
            self,
            places: List[Dict],
            user_interests: List[str]
    ) -> List[Dict]:
        """
        Rank places based on user interests

        Args:
            places: List of place dictionaries
            user_interests: List of user interest keywords

        Returns:
            Ranked list of places
        """
        # TODO: Implement actual ML-based ranking
        return self._mock_ranking(places, user_interests)

    def _mock_ranking(
            self,
            places: List[Dict],
            user_interests: List[str]
    ) -> List[Dict]:
        """Simple mock ranking based on category match"""

        # Interest to category mapping
        interest_mapping = {
            'تاریخی': ['HISTORICAL', 'RELIGIOUS', 'CULTURAL'],
            'فرهنگی': ['CULTURAL', 'HISTORICAL'],
            'طبیعت': ['NATURAL', 'RECREATIONAL'],
            'خانوادگی': ['RECREATIONAL', 'NATURAL'],
            'مذهبی': ['RELIGIOUS'],
            'غذا': ['DINING']
        }

        # Get relevant categories
        relevant_categories = []
        for interest in user_interests:
            relevant_categories.extend(interest_mapping.get(interest, []))

        # Score places
        scored_places = []
        for place in places:
            score = 0

            # Category match
            if place['category'] in relevant_categories:
                score += 10

            # Rating boost
            score += place.get('rating', 0) * 2

            # Free places get bonus for budget travelers
            if place.get('price_tier') == 'FREE':
                score += 3

            scored_places.append((score, place))

        # Sort by score descending
        scored_places.sort(reverse=True, key=lambda x: x[0])

        return [place for score, place in scored_places]

