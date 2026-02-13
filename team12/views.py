from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required
from rest_framework.views import APIView
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Place, Region
from .score import *
from .data_manager import *
import json

TEAM_NAME = "team12"

@api_login_required
@require_http_methods(["GET"])
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

def error_response(message, code="INVALID_PARAMETER", status=400):
    return JsonResponse({"error": {"code": code, "message": message}}, status=status)

@method_decorator(api_login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class ScoreCandidatePlacesView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            candidate_ids = data.get('candidate_place_ids', [])
            if not candidate_ids:
                return error_response("Invalid input")

            style = data.get('travel_style')
            budget = data.get('budget_level')
            season = data.get('season')
            duration = data.get('duration')

            places = get_or_enrich_places(candidate_ids)
            if not places:
                return JsonResponse({"scored_places": []}, status=200)

            score_map = {p.place_id: 1.0 for p in places}
            place_reasons = {p.place_id: p.ai_reason for p in places}
            applied_any = False

            if style:
                applied_any = True
                if style.upper() in styleIndex:
                    for p_id, val in scoreByStyle(places, style.upper()):
                        score_map[p_id] *= val

            if budget:
                applied_any = True
                if budget.upper() in budgetIndex:
                    for p_id, val in scoreByBudget(places, budget.upper()):
                        score_map[p_id] *= val

            if season:
                applied_any = True
                if season.upper() in seasonIndex:
                    for p_id, val in scoreBySeason(places, season.upper()):
                        score_map[p_id] *= val

            if duration:
                try:
                    d_val = float(duration)
                    if d_val > 0:
                        applied_any = True
                        for p_id, val in scoreByDuration(places, d_val):
                            score_map[p_id] *= val
                except:
                    pass

            applied_any = True
            try:
                for p_id, val in scoreByBaseRate(places):
                    score_map[p_id] *= val
            except:
                pass

            scored_places = []
            for p_id, total in score_map.items():
                final_val = total if applied_any else 1.0
                scored_places.append({
                    "place_id": p_id,
                    "score": round(final_val, 4),
                    "ai_reason": place_reasons.get(p_id) or "پیشنهاد بر اساس تحلیل محتوایی"
                })

            scored_places.sort(key=lambda x: x['score'], reverse=True)
            return JsonResponse({"scored_places": scored_places}, status=200)

        except Exception as e:
            return error_response(str(e), code="INTERNAL_ERROR", status=500)

class SuggestRegionsView(APIView):
    def get(self, request):
        try:
            regions = Region.objects.all()
            destinations = []
            for r in regions:
                destinations.append({
                    "region_id": r.region_id,
                    "region_name": r.region_name,
                    "match_score": 0.85,
                    "cover_image": f"https://example.com/images/{r.region_id}.jpg",
                    "ai_reason": "منطقه‌ای عالی برای سفر شما"
                })
            return JsonResponse({"destinations": destinations}, status=200)
        except Exception as e:
            return error_response(str(e), code="INTERNAL_ERROR", status=500)

class SuggestPlacesInRegionView(APIView):
    def get(self, request, region_id):
        try:
            places = Place.objects.filter(region__region_id=region_id)
            scored = []
            for p in places:
                scored.append({
                    "place_id": p.place_id,
                    "score": 0.9,
                    "ai_reason": p.ai_reason or "مکان پیشنهادی در این منطقه"
                })
            return JsonResponse({"region_id": region_id, "scored_places": scored}, status=200)
        except Exception as e:
            return error_response(str(e), code="INTERNAL_ERROR", status=500)