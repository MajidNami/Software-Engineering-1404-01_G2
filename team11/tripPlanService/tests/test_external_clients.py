
from django.test import TestCase
from unittest.mock import patch, MagicMock
from externalServices.grpc.services.facility_client import FacilityClient
from externalServices.grpc.services.recommendation_client import RecommendationClient

class ExternalClientsTest(TestCase):

    def setUp(self):
        self.facility_client = FacilityClient(base_url='http://test-api', use_mocks=False)
        self.recom_client = RecommendationClient(base_url='http://test-api', use_mocks=False)

    @patch('requests.post')
    def test_facility_search_places(self, mock_post):
        """Test searching places calls correct API"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'results': [
                {
                    'fac_id': 101,
                    'name_fa': 'Test Place',
                    'category': 'hotel',
                    'price_tier': 'moderate'
                }
            ]
        }
        mock_post.return_value = mock_response

        # Call method
        results = self.facility_client.search_places(province='Tehran', budget_level='MEDIUM')

        # Verify API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn('http://test-api/facilities/search/', args[0])
        self.assertEqual(kwargs['json']['province'], 'Tehran')
        self.assertEqual(kwargs['json']['price_tier'], 'moderate')

        # Verify Result Mapping
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], '101')
        self.assertEqual(results[0]['title'], 'Test Place')
        self.assertEqual(results[0]['price_tier'], 'MODERATE')

    @patch('requests.get')
    def test_facility_get_by_id(self, mock_get):
        """Test getting place by ID"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'fac_id': 101,
            'name_fa': 'Test Place',
            'category': 'hotel'
        }
        mock_get.return_value = mock_response

        result = self.facility_client.get_place_by_id('101')
        
        mock_get.assert_called_once_with('http://test-api/facilities/101/', timeout=5)
        self.assertEqual(result['title'], 'Test Place')

    @patch('requests.post')
    def test_recom_get_scored_places(self, mock_post):
        """Test API 1: Scoring places"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'scored_places': [
                {'place_id': 'p1', 'score': 95.5}
            ]
        }
        mock_post.return_value = mock_response

        result = self.recom_client.get_scored_places(['p1'], 'SOLO', 'MEDIUM', 3)
        
        self.assertEqual(result['p1'], 95.5)
        self.assertIn('http://test-api/recommendations/score-places/', mock_post.call_args[0][0])

    def test_fallback_to_mocks(self):
        """Test that use_mocks=True returns mock data without network calls"""
        mock_client = FacilityClient(use_mocks=True)
        results = mock_client.search_places(province='اصفهان')
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]['title'], 'میدان نقش جهان')

    @patch('requests.post')
    def test_network_failure_fallback(self, mock_post):
        """Test that exception triggers fallback"""
        mock_post.side_effect = Exception("Network Error")
        
        # Should gracefully return mock data
        results = self.facility_client.search_places(province='اصفهان')
        self.assertTrue(len(results) > 0)
