import os

import requests

TRIP_PLAN_REST_URL=os.getenv("TRIP_PLAN_REST_URL", "localhost:59007")

class TripPlanClient:
    @staticmethod
    def test_client():
        url = f'http://{TRIP_PLAN_REST_URL}/'
        response = requests.get(url)
        if response.status_code == 200:
            return str(response.text)
        else:
            return str(response.status_code)+"  "+url
