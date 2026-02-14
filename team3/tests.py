from django.test import TestCase


class TeamPingTests(TestCase):
    databases = {"default", "team3"}

    def test_ping_requires_auth(self):
        res = self.client.get("/team3/ping/")
        self.assertEqual(res.status_code, 401)


class RecommendationApiTests(TestCase):
    databases = {"default", "team3"}

    def test_personalized_returns_at_least_five_items(self):
        payload = {"userId": "u100", "destination": "tehran", "limit": 5}
        res = self.client.post("/team3/api/recommendations/personalized/", payload, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data["recommendations"]), 5)

    def test_guest_location_recommendations_do_not_persist_context(self):
        payload = {"latitude": 35.6892, "longitude": 51.3890, "radius_km": 50, "limit": 5}
        res = self.client.post("/team3/api/recommendations/location/", payload, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data["recommendations"]), 5)
        self.assertTrue(all(item["radius_km"] <= 100 for item in data["recommendations"]))

    def test_feedback_endpoint_accepts_like_and_dislike(self):
        rec_res = self.client.post(
            "/team3/api/recommendations/personalized/",
            {"userId": "u101", "destination": "shiraz", "limit": 5},
            content_type="application/json",
        )
        recommendation_id = rec_res.json()["recommendations"][0]["recommendation_id"]

        like_res = self.client.post(
            "/team3/api/feedback/",
            {"userId": "u101", "recommendation_id": recommendation_id, "value": 1},
            content_type="application/json",
        )
        self.assertEqual(like_res.status_code, 200)

        dislike_res = self.client.post(
            "/team3/api/feedback/",
            {"userId": "u101", "recommendation_id": recommendation_id, "value": -1},
            content_type="application/json",
        )
        self.assertEqual(dislike_res.status_code, 200)

    def test_feedback_invalid_recommendation_returns_404(self):
        res = self.client.post(
            "/team3/api/feedback/",
            {"userId": "u101", "recommendation_id": "rec_missing", "value": 1},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 404)
