from django.http import JsonResponse
from business.services import TripService

def test(request):
    trips = TripService.get_trips()
    return JsonResponse({
        "status": "ok",
        "count": len(trips),
        "trips": [
            {"id": str(t.trip_id), "title": t.title, "province": t.province}
            for t in trips
        ]
    })

def ok(request):
    trips = TripService.get_trips()
    return JsonResponse({
        "response": "ok and fine"
    })
