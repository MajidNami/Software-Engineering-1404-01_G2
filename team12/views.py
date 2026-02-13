from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Place, Region
from .score import *
import json
from django.views.decorators.csrf import csrf_exempt



TEAM_NAME = "team12"
CORE_BASE = settings.CORE_BASE_URL.rstrip('/')   # http://core:8000


@api_login_required
@require_http_methods(["GET"])
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")



# Helper to format error responses as per OpenAPI schema
def error_response(message, code="INVALID_PARAMETER", status=400):
    return JsonResponse({
        "error": {
            "code": code,
            "message": message
        }
    }, status=status)

@method_decorator(api_login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ScoreCandidatePlacesView(APIView):
    """
    POST /team12/recommend/places/score
    Evaluates and ranks candidate place IDs.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", "PARSE_ERROR")

        # 1. Validation and Mapping (YAML uses snake_case)
        candidate_ids = data.get('candidate_place', [])
        style = data.get('travel_style')
        budget = data.get('budget_level')
        season = data.get('season')
        duration = data.get('trip_duration')

        if not all([candidate_ids, style, budget, season, duration]):
            return error_response("Missing required fields: candidate_place, travel_style, budget_level, season, trip_duration")

        # 2. Query Candidates
        places = Place.objects.filter(place_id__in=candidate_ids)
        if not places.exists():
            return JsonResponse({"scored_places": []})

        # 3. Calculation
        score_map = {p.place_id: 1.0 for p in places}
        
        # Scoring logic using your score.py matrices
        for p_id, val in scoreByStyle(places, style.upper()): score_map[p_id] *= val
        for p_id, val in scoreByBudget(places, budget.upper()): score_map[p_id] *= val
        for p_id, val in scoreBySeason(places, season.upper()): score_map[p_id] *= val
        for p_id, val in scoreByDuration(places, duration): score_map[p_id] *= val

        # 4. Final Response Construction
        scored_places = []
        for p_id, total in score_map.items():
            scored_places.append({
                "place_id": p_id,
                "score": round(total, 4),
                "ai_reason": "با توجه به سبک سفر و بودجه شما، این مکان در این فصل بسیار توصیه می‌شود."
            })

        scored_places.sort(key=lambda x: x['score'], reverse=True)
        return JsonResponse({"scored_places": scored_places})

@method_decorator(api_login_required, name='dispatch')
class SuggestRegionsView(APIView):
    """
    GET /team12/recommend/regions
    Suggests best regions based on season and budget.
    """
    def get(self, request):
        # YAML specifies these as query parameters
        season = request.GET.get('season')
        budget = request.GET.get('budget_level')
        limit = int(request.GET.get('limit', 10))

        if not season or not budget:
            return error_response("Parameters 'season' and 'budget_level' are required.")

        # Logic: Average seasonal/budget score for all places in a region
        regions = Region.objects.all()
        destinations = []

        for region in regions:
            places = region.places.all()
            if not places.exists(): continue
            
            # Simple averaging logic for example
            avg_score = sum([1.0 for _ in places]) / places.count() # Replace with matrix logic if needed
            
            destinations.append({
                "region_id": region.region_id,
                "region_name": region.region_name,
                "match_score": round(avg_score, 4),
                "image_url": "https://api.core-domain.com/static/region.jpg",
                "ai_reason": f"این منطقه در فصل {season} برای بودجه {budget} مناسب است."
            })

        destinations.sort(key=lambda x: x['match_score'], reverse=True)
        return JsonResponse({"destinations": destinations[:limit]})

@method_decorator(api_login_required, name='dispatch')
class SuggestPlacesInRegionView(APIView):
    """
    GET /team12/recommend/regions/{region_id}/places
    Scores all places inside a specific region.
    """
    def get(self, request, region_id):
        # Query Params
        style = request.GET.get('travel_style')
        budget = request.GET.get('budget_level')
        season = request.GET.get('season')
        duration = request.GET.get('trip_duration')
        limit = int(request.GET.get('limit', 10))

        places = Place.objects.filter(region__region_id=region_id)
        if not places.exists():
            return error_response("Region not found or has no places", "NOT_FOUND", status=404)

        # Scoring Logic (Reusing your matrix logic)
        score_map = {p.place_id: 1.0 for p in places}
        # ... (Call your scoreBy functions here) ...

        scored_places = []
        for p_id, total in score_map.items():
            scored_places.append({
                "place_id": p_id,
                "score": round(total, 4),
                "ai_reason": "جاذبه برتر در این منطقه با توجه به معیارهای شما."
            })

        scored_places.sort(key=lambda x: x['score'], reverse=True)
        return JsonResponse({
            "region_id": region_id,
            "scored_places": scored_places[:limit]
        })
