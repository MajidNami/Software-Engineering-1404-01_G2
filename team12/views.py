from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Place, Region
from .score import *
from .data_manager import *
import json

TEAM_NAME = "team12"


@require_http_methods(["GET"])
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")


def error_response(message, code="INVALID_PARAMETER", status=400):
    return JsonResponse({"error": {"code": code, "message": message}}, status=status)


@method_decorator(csrf_exempt, name='dispatch')
class ScoreCandidatePlacesView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            candidate_ids = data.get('candidate_place_ids', [])
            if not candidate_ids:
                return error_response("Empty candidate list")

            if not isinstance(candidate_ids, list):
                return error_response("candidate_place_ids must be a list")

            style = data.get('travel_style', 'FAMILY')
            budget = data.get('budget_level', 'MODERATE')
            season = data.get('season', 'SPRING')
            # Match parameter name from team12.yaml
            duration = data.get('trip_duration_days', 1)

            places = get_or_enrich_places(candidate_ids)

            # Scoring Logic
            sc_style = dict(scoreByStyle(places, style))
            sc_season = dict(scoreBySeason(places, season))
            sc_budget = dict(scoreByBudget(places, budget))
            sc_duration = dict(scoreByDuration(places, duration))
            sc_base = dict(scoreByBaseRate(places))

            scored_list = []
            for p in places:
                pid = p.place_id
                # Weighted average scoring
                final_score = (
                        sc_style.get(pid, 0.5) * 0.4 +
                        sc_season.get(pid, 0.5) * 0.15 +
                        sc_budget.get(pid, 0.5) * 0.15 +
                        sc_duration.get(pid, 0.5) * 0.1 +
                        sc_base.get(pid, 0.5) * 0.2
                )
                scored_list.append({
                    "place_id": pid,
                    "score": round(final_score, 3),
                    "ai_reason": p.ai_reason
                })

            scored_list.sort(key=lambda x: x['score'], reverse=True)
            return JsonResponse({"scored_places": scored_list}, status=200)

        except Exception as e:
            print(f"ERROR: ScoreView failed: {str(e)}")
            return error_response(str(e), code="INTERNAL_ERROR", status=500)


class SuggestRegionsView(APIView):
    def get(self, request):
        try:
            # Data from DataManager (DB or Mock)
            destinations = get_suggested_regions()
            return JsonResponse({"destinations": destinations}, status=200)
        except Exception as e:
            return error_response(str(e), code="INTERNAL_ERROR", status=500)


class SuggestPlacesInRegionView(APIView):
    def get(self, request, region_id):
        try:
            # Data from DataManager (DB or Mock)
            scored_places = get_places_by_region(region_id)
            if not scored_places:
                return error_response(f"Region {region_id} not found", code="NOT_FOUND", status=404)

            return JsonResponse({
                "region_id": region_id,
                "scored_places": scored_places
            }, status=200)
        except Exception as e:
            return error_response(str(e), code="INTERNAL_ERROR", status=500)