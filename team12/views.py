from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required
from django.utils.decorators import method_decorator
import requests
from .data_manager import *
from rest_framework.views import APIView
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .models import Place, Region
from .score import *
import json
from django.views.decorators.csrf import csrf_exempt

TEAM_NAME = "team12"
CORE_BASE = settings.CORE_BASE_URL.rstrip('/')   # http://core:8000
WIKI_SERVICE_URL = "http://wiki-service:8000/api/place-info/"
MEDIA_SERVICE_URL = "http://media-service:8000/api/stats/"

@api_login_required
@require_http_methods(["GET"])
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

# Helper to format error responses as per OpenAPI schema
def error_response(message, code="INVALID_PARAMETER", status=400):
    return JsonResponse({"error": {"code": code, "message": message}}, status=status)

def fetch_external_data(self, place_id):
    context = {"wiki": {}, "media": {}}
    try:
        wiki_res = requests.get(f"{WIKI_SERVICE_URL}?place_id={place_id}", timeout=2)
        if wiki_res.status_code == 200:
            context["wiki"] = wiki_res.json()

        media_res = requests.get(f"{MEDIA_SERVICE_URL}?place_id={place_id}", timeout=2)
        if media_res.status_code == 200:
            context["media"] = media_res.json()
    except Exception as e:
        print(f"Error fetching from external services: {e}")
    
    return context

@method_decorator(api_login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ScoreCandidatePlacesView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return error_response("Invalid JSON format", "PARSE_ERROR")

        candidate_ids = data.get('candidate_place_ids', [])
        style = data.get('travel_style')
        budget = data.get('budget_level')
        season = data.get('season')
        duration = data.get('trip_duration_days')

        if not candidate_ids:
            return JsonResponse({"scored_places": []})

        places = get_or_enrich_places(candidate_place_ids)
        if not places.exists():
            return JsonResponse({"scored_places": []})

        score_map = {p.place_id: 1.0 for p in places}
        applied_any = False

        

        if style:
            style = str(style).upper()
            if style not in styleIndex:
                return error_response(f"Invalid travel_style: {style}. Options: {list(styleIndex.keys())}")

            applied_any = True
            for p_id, val in scoreByStyle(places, style):
                score_map[p_id] *= val

        if budget:
            budget = str(budget).upper()
            if budget not in budgetIndex:
                return error_response(f"Invalid budget_level: {budget}. Options: {list(budgetIndex.keys())}")

            applied_any = True
            for p_id, val in scoreByBudget(places, budget):
                score_map[p_id] *= val

        if season:
            season = str(season).upper()
            if season not in seasonIndex:
                return error_response(f"Invalid season: {season}. Options: {list(seasonIndex.keys())}")

            applied_any = True
            for p_id, val in scoreBySeason(places, season):
                score_map[p_id] *= val

        if duration:
            try:
                dur_val = float(duration)
                if dur_val > 0:
                    applied_any = True
                    for p_id, val in scoreByDuration(places, dur_val):
                        score_map[p_id] *= val
                else:
                    return error_response("trip_duration_days must be positive")
            except (ValueError, TypeError):
                return error_response("trip_duration_days must be a number")

        applied_any = True 
        for p_id, val in scoreByBaseRate(places):
            score_map[p_id] *= val

        scored_places = []
        for p_id, total in score_map.items():
            final_val = total if applied_any else 1.0
            scored_places.append({
                "place_id": p_id,
                "score": round(final_val, 4),
                "ai_reason": "Based on your provided preferences." if applied_any else "No preferences provided."
            })

        scored_places.sort(key=lambda x: x['score'], reverse=True)
        return JsonResponse({"scored_places": scored_places})


@method_decorator(api_login_required, name='dispatch')
class SuggestRegionsView(APIView):
    def get(self, request):
        season = request.GET.get('season')
        budget = request.GET.get('budget_level')
        limit_param = request.GET.get('limit', 10)

        try:
            limit = int(limit_param)
        except ValueError:
            limit = 10

        regions = Region.objects.all()
        destinations = []

        if season:
            season = season.upper()
            if season not in seasonIndex:
                return error_response("Invalid season")

        if budget:
            budget = budget.upper()
            if budget not in budgetIndex:
                return error_response("Invalid budget_level")

        for region in regions:
            places = region.places.all()
            if not places.exists(): continue

            region_score = 1.0
            applied_any = False

            total_base_rate_score = 0
            for p in places:
                total_base_rate_score += max(p.base_rate / 5.0, 0.1)
            
            avg_base_rate = total_base_rate_score / places.count()
            region_score *= avg_base_rate
            applied_any = True

            if season:
                applied_any = True
                total_s = 0
                target_s_idx = seasonIndex[season]
                for p in places:
                    p_s_idx = seasonIndex.get(p.season.upper(), 0)
                    total_s += seasonMtx[target_s_idx][p_s_idx]
                region_score *= (total_s / places.count())

            if budget:
                applied_any = True
                total_b = 0
                target_b_idx = budgetIndex[budget]
                for p in places:
                    p_b_idx = budgetIndex.get(p.budget_level.upper(), 0)
                    total_b += budgetMtx[target_b_idx][p_b_idx]
                region_score *= (total_b / places.count())

            if applied_any:
                destinations.append({
                    "region_id": region.region_id,
                    "region_name": region.region_name,
                    "match_score": round(region_score, 4),
                    "ai_reason": f"Recommended based on {season if season else ''} {budget if budget else ''}"
                })

        destinations.sort(key=lambda x: x['match_score'], reverse=True)

        return JsonResponse({"destinations": destinations[:limit]})


@method_decorator(api_login_required, name='dispatch')
class SuggestPlacesInRegionView(APIView):
    def get(self, request, region_id):
        style = request.GET.get('travel_style')
        budget = request.GET.get('budget_level')
        season = request.GET.get('season')
        duration = request.GET.get('trip_duration_days')

        try:
            limit = int(request.GET.get('limit', 10))
        except ValueError:
            limit = 10

        places = Place.objects.filter(region__region_id=region_id)
        if not places.exists():
            return error_response("Region not found", "NOT_FOUND", status=404)

        score_map = {p.place_id: 1.0 for p in places}
        applied_any = False

        if style:
            applied_any = True
            if style.upper() in styleIndex:
                for p_id, val in scoreByStyle(places, style.upper()): score_map[p_id] *= val

        if budget:
            applied_any = True
            if budget.upper() in budgetIndex:
                for p_id, val in scoreByBudget(places, budget.upper()): score_map[p_id] *= val

        if season:
            applied_any = True
            if season.upper() in seasonIndex:
                for p_id, val in scoreBySeason(places, season.upper()): score_map[p_id] *= val

        if duration:
            try:
                d_val = float(duration)
                if d_val > 0:
                    applied_any = True
                    for p_id, val in scoreByDuration(places, d_val): score_map[p_id] *= val
            except:
                pass


        applied_any = True
        for p_id, val in scoreByBaseRate(places):
            score_map[p_id] *= val

        scored_places = []
        for p_id, total in score_map.items():
            final_val = total if applied_any else 1.0
            scored_places.append({
                "place_id": p_id,
                "score": round(final_val, 4),
                "ai_reason": "Recommended place in this region."
            })

        scored_places.sort(key=lambda x: x['score'], reverse=True)
        return JsonResponse({
            "region_id": region_id,
            "scored_places": scored_places[:limit]
        })