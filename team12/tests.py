from django.test import TestCase
from unittest.mock import patch
from .models import Place, Region
from .data_manager import fetch_wiki_data, fetch_engagement_data, get_or_enrich_places

class Team12ServiceTests(TestCase):

    def test_ping_requires_auth(self):
        res = self.client.get("/team12/ping/")
        self.assertEqual(res.status_code, 401)

    @patch('requests.get')
    def test_fetch_wiki_data_mock(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "summary": "توضیحات تست سی‌وسه‌پل",
            "tags": ["تاریخی", "اصفهان"],
            "category": "تاریخی"
        }

        summary, tags, category = fetch_wiki_data("siosepol")
        
        self.assertEqual(summary, "توضیحات تست سی‌وسه‌پل")
        self.assertIn("تاریخی", tags)
        self.assertEqual(category, "تاریخی")

    @patch('requests.get')
    def test_fetch_engagement_data_mock(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "ratingSummary": {"avg": 4.5}
        }

        rate = fetch_engagement_data("siosepol")
        self.assertEqual(rate, 4.5)

    @patch('team12.data_manager.fetch_wiki_data')
    @patch('team12.data_manager.fetch_engagement_data')
    @patch('team12.data_manager.generate_ai_metadata_for_place')
    def test_get_or_enrich_places(self, mock_ai, mock_media, mock_wiki):
        mock_wiki.return_value = ("خلاصه ویکی", ["تگ۱"], "تاریخی")
        mock_media.return_value = 4.0
        mock_ai.return_value = {
            "duration": "3",
            "region_id": "isfahan-reg",
            "region_name": "اصفهان",
            "budget_level": "ECONOMY",
            "travel_style": "SOLO",
            "season": "SPRING",
            "ai_reason": "دلیل تست هوش مصنوعی"
        }

        place_ids = ["siosepol"]
        get_or_enrich_places(place_ids)

        place = Place.objects.get(place_id="siosepol")
        
        self.assertEqual(place.place_name, "Siosepol")
        self.assertEqual(place.base_rate, 4.0)
        self.assertEqual(place.duration, 3)
        self.assertEqual(place.travel_style, "SOLO")
        self.assertEqual(place.region.region_name, "اصفهان")
        