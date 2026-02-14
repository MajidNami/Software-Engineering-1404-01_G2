from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required

TEAM_NAME = "team9"

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")
def map_view(request):
    return render(request, f"{TEAM_NAME}/map.html")
def index_view(request):
    return render(request, 'team9/index.html')

from django.http import JsonResponse


'''def mock_facilities_api(request):
    data = [
        {"name": "رستوران البرز", "lat": 35.7000, "lng": 51.4000, "type": "restaurant"},
        {"name": "هتل آزادی", "lat": 35.7500, "lng": 51.3500, "type": "hotel"},
        {"name": "پارک ملت", "lat": 35.7800, "lng": 51.4100, "type": "park"},
    ]
    return JsonResponse(data, safe=False)
'''
