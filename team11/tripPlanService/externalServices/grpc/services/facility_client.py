"""
Facility Service Client - gRPC communication with Mohammad Hossein's service
"""
import grpc
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class FacilityClient:
    """
    Client for communicating with Facility Service via gRPC

    This service provides information about places, hotels, restaurants, and attractions.
    """

    def __init__(self, host: str = 'localhost', port: int = 50051):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self._connect()

    def _connect(self):
        """Establish gRPC connection"""
        try:
            self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
            logger.info(f"Connected to Facility Service at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Facility Service: {e}")
            self.stub = None

    def search_places(
            self,
            province: str,
            city: Optional[str] = None,
            categories: Optional[List[str]] = None,
            budget_level: Optional[str] = None,
            limit: int = 20
    ) -> List[Dict]:
        """
        Search for places based on criteria

        Returns list of places with: id, title, category, address, lat, lng,
        entry_fee, price_tier, description, images, opening_hours, rating
        """
        if not self.stub:
            return self._get_mock_places(province, city, categories, limit)

        try:
            # TODO: Implement actual gRPC call when ready
            return self._get_mock_places(province, city, categories, limit)

        except grpc.RpcError as e:
            logger.error(f"gRPC error in search_places: {e}")
            return self._get_mock_places(province, city, categories, limit)

    def get_place_by_id(self, place_id: str) -> Optional[Dict]:
        """Get detailed information about a specific place"""
        if not self.stub:
            return self._get_mock_place(place_id)

        try:
            # TODO: Implement actual gRPC call
            return self._get_mock_place(place_id)
        except grpc.RpcError as e:
            logger.error(f"gRPC error in get_place_by_id: {e}")
            return None

    def check_availability(
            self,
            place_id: str,
            date: str,
            start_time: str,
            end_time: str
    ) -> Dict:
        """Check if a place is available at a specific time"""
        if not self.stub:
            return {'is_available': True, 'reason': '', 'suggested_times': []}

        try:
            # TODO: Implement actual gRPC call
            return {'is_available': True, 'reason': '', 'suggested_times': []}
        except grpc.RpcError as e:
            logger.error(f"gRPC error in check_availability: {e}")
            return {'is_available': True, 'reason': '', 'suggested_times': []}

    def _get_mock_places(
            self,
            province: str,
            city: Optional[str],
            categories: Optional[List[str]],
            limit: int
    ) -> List[Dict]:
        """Mock data for development - replace with actual gRPC calls"""
        mock_places = [
            {
                'id': 'place_001',
                'title': 'میدان نقش جهان',
                'category': 'HISTORICAL',
                'address': 'اصفهان، میدان نقش جهان',
                'lat': 32.6546,
                'lng': 51.6777,
                'entry_fee': 200000,
                'price_tier': 'BUDGET',
                'description': 'یکی از بزرگترین میدان‌های جهان',
                'images': [],
                'opening_hours': {'daily': '08:00-22:00'},
                'rating': 4.8,
                'review_count': 1250
            },
            {
                'id': 'place_002',
                'title': 'مسجد شیخ لطف الله',
                'category': 'RELIGIOUS',
                'address': 'اصفهان، میدان نقش جهان',
                'lat': 32.6565,
                'lng': 51.6785,
                'entry_fee': 500000,
                'price_tier': 'MODERATE',
                'description': 'شاهکار معماری دوران صفوی',
                'images': [],
                'opening_hours': {'daily': '09:00-17:00'},
                'rating': 4.9,
                'review_count': 980
            },
            {
                'id': 'place_003',
                'title': 'رستوران سنتی شاهرزاد',
                'category': 'DINING',
                'address': 'اصفهان، خیابان چهارباغ',
                'lat': 32.6543,
                'lng': 51.6724,
                'entry_fee': 0,
                'price_tier': 'MODERATE',
                'description': 'رستوران سنتی با غذاهای محلی',
                'images': [],
                'opening_hours': {'daily': '12:00-23:00'},
                'rating': 4.5,
                'review_count': 450
            },
            {
                'id': 'hotel_001',
                'title': 'هتل عباسی',
                'category': 'STAY',
                'address': 'اصفهان، خیابان چهارباغ',
                'lat': 32.6565,
                'lng': 51.6750,
                'entry_fee': 5000000,
                'price_tier': 'LUXURY',
                'description': 'هتل تاریخی 5 ستاره',
                'images': [],
                'opening_hours': {'24/7': True},
                'rating': 4.7,
                'review_count': 820
            },
            {
                'id': 'place_004',
                'title': 'پل سی‌وسه‌پل',
                'category': 'HISTORICAL',
                'address': 'اصفهان، زاینده رود',
                'lat': 32.6479,
                'lng': 51.6698,
                'entry_fee': 0,
                'price_tier': 'FREE',
                'description': 'پل تاریخی دوران صفوی',
                'images': [],
                'opening_hours': {'24/7': True},
                'rating': 4.8,
                'review_count': 1520
            },
            {
                'id': 'place_005',
                'title': 'باغ چهلستون',
                'category': 'CULTURAL',
                'address': 'اصفهان، خیابان استانداری',
                'lat': 32.6612,
                'lng': 51.6697,
                'entry_fee': 150000,
                'price_tier': 'BUDGET',
                'description': 'کاخ موزه با باغ زیبا',
                'images': [],
                'opening_hours': {'daily': '08:30-18:00'},
                'rating': 4.6,
                'review_count': 750
            },
            {
                'id': 'restaurant_001',
                'title': 'رستوران هتل عباسی',
                'category': 'DINING',
                'address': 'اصفهان، هتل عباسی',
                'lat': 32.6570,
                'lng': 51.6755,
                'entry_fee': 0,
                'price_tier': 'EXPENSIVE',
                'description': 'رستوران لوکس با غذاهای بین‌المللی',
                'images': [],
                'opening_hours': {'daily': '07:00-23:00'},
                'rating': 4.6,
                'review_count': 320
            },
            {
                'id': 'restaurant_002',
                'title': 'کافه آرت اصفهان',
                'category': 'DINING',
                'address': 'اصفهان، خیابان چهارباغ',
                'lat': 32.6540,
                'lng': 51.6730,
                'entry_fee': 0,
                'price_tier': 'BUDGET',
                'description': 'کافه هنری با فضای دنج',
                'images': [],
                'opening_hours': {'daily': '10:00-23:00'},
                'rating': 4.3,
                'review_count': 280
            },
        ]

        # Filter by province/city
        filtered = [p for p in mock_places if province in p['address']]
        if city:
            filtered = [p for p in filtered if city in p['address']]

        # Filter by categories
        if categories:
            filtered = [p for p in filtered if p['category'] in categories]

        return filtered[:limit]

    def _get_mock_place(self, place_id: str) -> Optional[Dict]:
        """Get mock place by ID"""
        places = self._get_mock_places('', None, None, 100)
        for place in places:
            if place['id'] == place_id:
                return place
        return None

    def close(self):
        """Close gRPC connection"""
        if self.channel:
            self.channel.close()
            logger.info("Closed connection to Facility Service")
