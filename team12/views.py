from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required
from .models import Place
from .score import *
import json
from django.views.decorators.csrf import csrf_exempt

TEAM_NAME = "team12"

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

@api_login_required
@csrf_exempt
def get_recommendations(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            user_style = data.get('Travel_style')
            user_budget = data.get('Budget_level')
            user_duration = data.get('Trip_duration')
            candidate_ids = data.get('candidate_place', []) 

            places = Place.objects.filter(place_id__in=candidate_ids)
            
            # Start with a base score of 1.0 for multiplication
            score_map = {p.place_id: 1.0 for p in places}
            applied_any_score = False

            # 1. Style Scoring
            if user_style:
                applied_any_score = True
                for p_id, val in scoreByStyle(places, user_style):
                    score_map[p_id] *= val
            
            # 2. Budget Scoring
            if user_budget:
                applied_any_score = True
                for p_id, val in scoreByBudget(places, user_budget):
                    score_map[p_id] *= val

            # 3. Duration Scoring
            if user_duration:
                applied_any_score = True
                for p_id, val in scoreByDuration(places, user_duration):
                    score_map[p_id] *= val

            scored_places = []
            for p_id, total in score_map.items():
                # If no metrics were provided, we should probably return 0 or a neutral score
                final_val = total if applied_any_score else 0.0
                scored_places.append({
                    "place_id": p_id,
                    "score": round(final_val, 4)
                })

            # Sort by score descending
            scored_places.sort(key=lambda x: x['score'], reverse=True)

            return JsonResponse({"scored_places": scored_places})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)