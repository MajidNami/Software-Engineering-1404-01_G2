from django.contrib.auth import get_user_model
from django.test import TestCase

from team5.models import Team5City, Team5Media, Team5MediaRating, Team5Place

User = get_user_model()


class TeamPingTests(TestCase):
    def test_ping_requires_auth(self):
        res = self.client.get("/team5/ping/")
        self.assertEqual(res.status_code, 401)


class Team5RecommendationApiTests(TestCase):
    databases = {"default", "team5"}

    @classmethod
    def setUpTestData(cls):
        Team5City.objects.create(city_id="tehran", city_name="Tehran", latitude=35.6892, longitude=51.389)
        Team5Place.objects.create(
            place_id="tehran-azadi-tower",
            city_id="tehran",
            place_name="Azadi Tower",
            latitude=35.6997,
            longitude=51.338,
        )
        Team5Place.objects.create(
            place_id="tehran-milad-tower",
            city_id="tehran",
            place_name="Milad Tower",
            latitude=35.7448,
            longitude=51.3753,
        )
        Team5Media.objects.create(
            media_id="m3",
            place_id="tehran-azadi-tower",
            title="Azadi Tower in winter",
            caption="Night lights and city skyline",
        )
        Team5Media.objects.create(
            media_id="m9",
            place_id="tehran-milad-tower",
            title="Milad Tower panoramic deck",
            caption="Tehran skyline from the top of the tower",
        )

        cls.user_main = User.objects.create_user(email="main.user@test.com", password="Pass1234!Strong")
        cls.user_second = User.objects.create_user(email="second.user@test.com", password="Pass1234!Strong")
        extra_users = [
            User.objects.create_user(email=f"extra{i}@test.com", password="Pass1234!Strong")
            for i in range(1, 5)
        ]

        Team5MediaRating.objects.create(
            user_id=cls.user_main.id,
            user_email=cls.user_main.email,
            media_id="m3",
            rate=5.0,
            liked=True,
        )
        Team5MediaRating.objects.create(
            user_id=cls.user_main.id,
            user_email=cls.user_main.email,
            media_id="m9",
            rate=2.5,
            liked=False,
        )
        Team5MediaRating.objects.create(
            user_id=cls.user_second.id,
            user_email=cls.user_second.email,
            media_id="m3",
            rate=4.5,
            liked=True,
        )
        for user in extra_users:
            Team5MediaRating.objects.create(
                user_id=user.id,
                user_email=user.email,
                media_id="m3",
                rate=4.0,
                liked=True,
            )

    def test_cities_contract(self):
        res = self.client.get("/team5/api/cities/")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertTrue(len(payload) > 0)
        self.assertIn("cityId", payload[0])
        self.assertIn("cityName", payload[0])
        self.assertIn("coordinates", payload[0])

    def test_city_places_filtered_by_city(self):
        res = self.client.get("/team5/api/places/city/tehran/")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertTrue(len(payload) > 0)
        self.assertTrue(all(item["cityId"] == "tehran" for item in payload))

    def test_popular_recommendations_obey_threshold(self):
        res = self.client.get("/team5/api/recommendations/popular/?limit=50")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertEqual(payload["kind"], "popular")
        self.assertTrue(len(payload["items"]) > 0)
        self.assertEqual(payload["items"][0]["mediaId"], "m3")
        for item in payload["items"]:
            self.assertGreaterEqual(item["overallRate"], 4.0)
            self.assertGreaterEqual(item["ratingsCount"], 5)

    def test_nearest_recommendations_with_city_override(self):
        res = self.client.get("/team5/api/recommendations/nearest/?cityId=tehran&limit=10")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertEqual(payload["kind"], "nearest")
        self.assertEqual(payload["title"], "your nearest")
        self.assertEqual(payload["source"], "manual_city_override")
        self.assertEqual(payload["cityId"], "tehran")
        self.assertGreaterEqual(payload["count"], 1)
        self.assertTrue(all(item["matchReason"] == "your_nearest" for item in payload["items"]))

    def test_nearest_recommendations_requires_resolvable_location(self):
        res = self.client.get("/team5/api/recommendations/nearest/")
        self.assertEqual(res.status_code, 400)
        payload = res.json()
        self.assertEqual(payload["kind"], "nearest")
        self.assertEqual(payload["source"], "unresolved")

    def test_personalized_recommendations_rank_for_user(self):
        res = self.client.get(f"/team5/api/recommendations/personalized/?userId={self.user_main.id}&limit=10")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertEqual(payload["source"], "personalized")
        self.assertEqual(payload["userId"], str(self.user_main.id))
        self.assertGreaterEqual(len(payload["items"]), 1)
        self.assertEqual(payload["highRatedItems"][0]["mediaId"], "m3")

    def test_personalized_fallback_for_new_user(self):
        fresh = User.objects.create_user(email="brand.new@test.com", password="Pass1234!Strong")
        res = self.client.get(f"/team5/api/recommendations/personalized/?userId={fresh.id}")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertEqual(payload["source"], "fallback_popular")
        self.assertGreater(len(payload["items"]), 0)

    def test_personalized_requires_user_id(self):
        res = self.client.get("/team5/api/recommendations/personalized/")
        self.assertEqual(res.status_code, 400)

    def test_user_interest_distribution(self):
        res = self.client.get(f"/team5/api/users/{self.user_main.id}/interests/")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertEqual(payload["userId"], str(self.user_main.id))
        self.assertIn("cityInterests", payload)
        self.assertIn("placeInterests", payload)
        self.assertGreaterEqual(len(payload["cityInterests"]), 1)

    def test_list_registered_users(self):
        res = self.client.get("/team5/api/users/")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertIn("count", payload)
        self.assertIn("items", payload)
        self.assertGreaterEqual(payload["count"], 2)

    def test_user_ratings_endpoint_from_db(self):
        res = self.client.get(f"/team5/api/users/{self.user_main.id}/ratings/")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertEqual(str(self.user_main.id), payload["userId"])
        self.assertEqual(payload["count"], 2)
        self.assertEqual(payload["items"][0]["mediaId"], "m3")

    def test_media_split_high_low(self):
        res = self.client.get(f"/team5/api/media/?userId={self.user_main.id}")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertTrue(any(item["mediaId"] == "m3" for item in payload["ratedHigh"]))
        self.assertTrue(any(item["mediaId"] == "m9" for item in payload["ratedLow"]))

    def test_personalized_contains_similar_items(self):
        res = self.client.get(f"/team5/api/recommendations/personalized/?userId={self.user_main.id}&limit=6")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertTrue(any(item["mediaId"] == "m3" for item in payload["highRatedItems"]))
        self.assertTrue(any(item["mediaId"] == "m9" for item in payload["similarItems"]))
