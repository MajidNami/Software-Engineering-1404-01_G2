"""
Wikipedia/Knowledge Base Client
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class WikiClient:
    """
    Client for fetching place information from Wikipedia or knowledge base
    """

    def __init__(self):
        logger.info("WikiClient initialized")

    def get_place_info(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a place from Wikipedia

        Args:
            place_id: Place identifier

        Returns:
            {
                'title': str,
                'description': str,
                'history': str,
                'images': List[str],
                'wiki_url': str
            }
        """
        # TODO: Implement actual API call to Wikipedia or knowledge base
        return self._get_mock_info(place_id)

    def _get_mock_info(self, place_id: str) -> Optional[Dict]:
        """Mock data for development"""
        mock_data = {
            'place_001': {
                'title': 'میدان نقش جهان',
                'description': 'میدان نقش جهان یکی از بزرگترین میدان‌های جهان و از آثار به‌جای‌مانده از دوره صفوی در شهر اصفهان است.',
                'history': 'این میدان در زمان شاه عباس اول ساخته شد و مرکز شهر جدید اصفهان بود.',
                'images': [
                    'https://example.com/naghsh-jahan-1.jpg',
                    'https://example.com/naghsh-jahan-2.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/میدان_نقش_جهان'
            },
            'place_002': {
                'title': 'مسجد شیخ لطف‌الله',
                'description': 'مسجد شیخ لطف‌الله یکی از شاهکارهای معماری اسلامی دوره صفوی است.',
                'history': 'این مسجد بین سال‌های 1603 تا 1619 میلادی ساخته شد.',
                'images': [
                    'https://example.com/lotfollah-1.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/مسجد_شیخ_لطف‌الله'
            }
        }
        return mock_data.get(place_id)