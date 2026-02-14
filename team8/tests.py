from django.test import TestCase

class TeamPingTests(TestCase):
    def test_ping_requires_auth(self):
        res = self.client.get("/team8/ping/")
        self.assertEqual(res.status_code, 401)
