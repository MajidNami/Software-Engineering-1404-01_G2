import hashlib
import json
import time
import uuid

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from core.auth import api_login_required

from .models import Feedback, LocationContext, Recommendation, UserInteraction, UserProfileFeature

TEAM_NAME = "team3"

POPULAR_ITEMS = [
    {"id": "popular_place_1", "type": "place", "title": "Golestan Palace"},
    {"id": "popular_place_2", "type": "place", "title": "Naqsh-e Jahan"},
    {"id": "popular_place_3", "type": "place", "title": "Persepolis"},
    {"id": "popular_event_1", "type": "event", "title": "Nowruz Festival"},
    {"id": "popular_route_1", "type": "route", "title": "Caspian Coast Route"},
]


def _json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


def _stable_score(seed_text):
    digest = hashlib.sha256(seed_text.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def _clamp_limit(raw_limit, default_limit=10, min_limit=1):
    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        limit = default_limit
    return max(min_limit, min(limit, 50))


def _get_user_id(request, payload):
    if request.user.is_authenticated and request.user.username:
        return request.user.username
    return payload.get("user_id") or payload.get("userId")


def _get_user_features(user_id):
    return list(UserProfileFeature.objects.filter(user_id=user_id).values_list("category", "weight"))


def _get_user_interactions(user_id):
    return list(
        UserInteraction.objects.filter(user_id=user_id).values("item_id", "item_type", "interaction_type")
    )


def _get_search_terms(user_id):
    return list(
        UserInteraction.objects.filter(user_id=user_id, interaction_type="search").values_list("item_id", flat=True)
    )


def _feedback_bias(user_id, item_id):
    rec = (
        Recommendation.objects.filter(
            user_id=user_id,
            item_id=item_id,
            user_feedback__in=[Recommendation.FEEDBACK_LIKE, Recommendation.FEEDBACK_DISLIKE],
        )
        .order_by("-feedback_at", "-generated_at")
        .first()
    )
    if not rec:
        return 0.0
    if rec.user_feedback == Recommendation.FEEDBACK_LIKE:
        return 0.18
    if rec.user_feedback == Recommendation.FEEDBACK_DISLIKE:
        return -0.45
    return 0.0


def _build_recommendation(user_id, item, reason_type, reason_description, score):
    return Recommendation.objects.create(
        recommendation_id=f"rec_{uuid.uuid4().hex[:12]}",
        user_id=user_id,
        item_id=item["id"],
        item_type=item["type"],
        score=score,
        reason_type=reason_type,
        reason_description=reason_description,
    )


def _recommendation_to_dto(rec, title=None, meta=None):
    return {
        "recommendation_id": rec.recommendation_id,
        "item_id": rec.item_id,
        "item_type": rec.item_type,
        "title": title or rec.item_id,
        "score": round(rec.score, 3),
        "reason": rec.reason_description,
        "meta": meta or {},
    }


def _generate_candidates(destination, season, context):
    base_items = [
        {"id": f"{destination}_place_1", "type": "place", "title": f"{destination} view point"},
        {"id": f"{destination}_event_1", "type": "event", "title": f"{season} festival in {destination}"},
        {"id": f"{destination}_route_1", "type": "route", "title": f"{destination} city route"},
        {"id": f"{destination}_article_1", "type": "article", "title": f"{destination} travel guide"},
        {"id": f"{destination}_place_2", "type": "place", "title": f"best cafes in {destination}"},
        {"id": f"{destination}_place_3", "type": "place", "title": f"historic area of {destination}"},
    ]
    extra = context.get("candidate_items") or []
    return base_items + extra


def _popular_candidates(limit):
    return POPULAR_ITEMS[: max(limit, 5)]


def _rank_candidates(user_id, candidates):
    interests = _get_user_features(user_id)
    interest_terms = {category.lower() for category, _ in interests}
    search_terms = {term.lower() for term in _get_search_terms(user_id)}
    ranked = []
    for item in candidates:
        item_title = item.get("title", "").lower()
        seed = f"{user_id}:{item['id']}:{item['type']}"
        base_score = _stable_score(seed)
        interest_boost = 0.15 if any(term in item_title for term in interest_terms) else 0.0
        search_boost = 0.12 if any(term in item_title for term in search_terms) else 0.0
        feedback_boost = _feedback_bias(user_id, item["id"])
        score = min(1.0, max(0.0, base_score + interest_boost + search_boost + feedback_boost))
        reason_type = "popularity"
        reason_description = "Suggested by popularity baseline."
        if interest_boost > 0:
            reason_type = "interest"
            reason_description = "Matched with your saved interests."
        elif search_boost > 0:
            reason_type = "interest"
            reason_description = "Related to your previous search activity."
        elif feedback_boost != 0:
            reason_description = "Adjusted by your previous feedback."
        ranked.append(
            {
                "item": item,
                "score": score,
                "reason_type": reason_type,
                "reason_description": reason_description,
            }
        )
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")


def health(request):
    return JsonResponse({"service": "Recommendation Service", "status": "ok"})


@csrf_exempt
def upsert_interests(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    payload = _json_body(request)
    user_id = _get_user_id(request, payload)
    interests = payload.get("interests", [])
    if not user_id or not isinstance(interests, list):
        return JsonResponse({"success": False}, status=400)
    now = timezone.now()
    for entry in interests:
        category = str(entry.get("category", "")).strip()
        weight = float(entry.get("weight", 0.5))
        if not category:
            continue
        UserProfileFeature.objects.update_or_create(
            feature_id=entry.get("feature_id") or f"f_{uuid.uuid4().hex[:10]}",
            defaults={
                "user_id": user_id,
                "category": category,
                "weight": max(0.0, min(weight, 1.0)),
                "source": UserProfileFeature.SOURCE_MANUAL,
                "updated_at": now,
            },
        )
    return JsonResponse({"success": True})


@csrf_exempt
def personalized_recommendations(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    started_at = time.perf_counter()
    payload = _json_body(request)
    user_id = _get_user_id(request, payload)
    destination = payload.get("destination") or payload.get("destinationId") or "iran"
    season = payload.get("season", "ALL")
    limit = _clamp_limit(payload.get("limit"), default_limit=10, min_limit=5)

    if not user_id:
        return JsonResponse({"recommendations": []}, status=400)

    interactions = _get_user_interactions(user_id)
    is_cold_start = not interactions and not _get_user_features(user_id)
    candidates = _popular_candidates(limit) if is_cold_start else _generate_candidates(destination, season, payload)
    ranked = _rank_candidates(user_id, candidates)[:limit]

    recs = []
    for entry in ranked:
        item = entry["item"]
        rec = _build_recommendation(
            user_id=user_id,
            item=item,
            reason_type=entry["reason_type"],
            reason_description=entry["reason_description"],
            score=entry["score"],
        )
        recs.append(_recommendation_to_dto(rec, title=item.get("title")))

    elapsed_ms = int((time.perf_counter() - started_at) * 1000)
    return JsonResponse({"recommendations": recs, "response_time_ms": elapsed_ms, "cold_start": is_cold_start})


@csrf_exempt
def recommendations_by_location(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    payload = _json_body(request)
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    radius_km = _clamp_limit(payload.get("radius_km"), default_limit=100, min_limit=1)
    user_id = _get_user_id(request, payload) or "guest"
    limit = _clamp_limit(payload.get("limit"), default_limit=10, min_limit=5)

    if latitude is None or longitude is None:
        return JsonResponse({"recommendations": []}, status=400)

    if request.user.is_authenticated and payload.get("persist_context") is True:
        LocationContext.objects.create(
            location_id=f"loc_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            latitude=float(latitude),
            longitude=float(longitude),
            radius_km=min(radius_km, 100),
        )

    candidates = [
        {
            "id": f"near_{i}",
            "type": "place",
            "title": f"Nearby place {i}",
        }
        for i in range(1, limit + 2)
    ]
    ranked = _rank_candidates(user_id, candidates)[:limit]
    items = []
    for entry in ranked:
        items.append(
            {
                "id": entry["item"]["id"],
                "type": entry["item"]["type"],
                "title": entry["item"]["title"],
                "score": round(entry["score"], 3),
                "radius_km": min(radius_km, 100),
                "reason": "Location-based recommendation",
            }
        )
    return JsonResponse({"recommendations": items})


@csrf_exempt
def contextual_recommendations(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    payload = _json_body(request)
    user_id = _get_user_id(request, payload)
    if not user_id:
        return JsonResponse({"recommendations": []}, status=400)

    context = payload.get("context", {})
    destination = context.get("destination") or payload.get("destination") or "iran"
    season = context.get("season") or payload.get("season", "ALL")
    limit = _clamp_limit(payload.get("limit"), default_limit=10, min_limit=3)

    candidates = _generate_candidates(destination, season, context)
    ranked = _rank_candidates(user_id, candidates)[:limit]
    recs = []
    for entry in ranked:
        item = entry["item"]
        rec = _build_recommendation(
            user_id=user_id,
            item=item,
            reason_type=entry["reason_type"],
            reason_description=entry["reason_description"],
            score=entry["score"],
        )
        recs.append(_recommendation_to_dto(rec, title=item.get("title")))
    return JsonResponse({"recommendations": recs})


@csrf_exempt
def score_candidates(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    payload = _json_body(request)
    user_id = _get_user_id(request, payload)
    candidate_ids = payload.get("candidate_place_ids", [])

    if not user_id or not candidate_ids:
        return JsonResponse({"scored_places": []})

    scored = []
    for place_id in candidate_ids:
        seed = f"{user_id}:{place_id}"
        score = _stable_score(seed) + _feedback_bias(user_id, place_id)
        scored.append(
            {
                "place_id": place_id,
                "score": round(max(0.0, min(score, 1.0)), 3),
                "reasoning_tag": "interest" if score > 0.6 else "popularity",
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return JsonResponse({"scored_places": scored})


@csrf_exempt
def suggest_destinations(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    payload = _json_body(request)
    user_id = _get_user_id(request, payload)
    limit = _clamp_limit(payload.get("limit"), default_limit=5, min_limit=1)
    regions = [
        ("tehran", "Tehran"),
        ("isfahan", "Isfahan"),
        ("shiraz", "Shiraz"),
        ("tabriz", "Tabriz"),
        ("kish", "Kish"),
        ("mashhad", "Mashhad"),
    ]

    suggestions = []
    for region_id, region_name in regions:
        score = _stable_score(f"{user_id}:{region_id}") if user_id else 0.5
        suggestions.append(
            {
                "region_id": region_id,
                "region_name": region_name,
                "match_score": round(score, 3),
                "image_url": "",
                "reason": "Suggested based on your profile and trend.",
            }
        )

    suggestions.sort(key=lambda x: x["match_score"], reverse=True)
    return JsonResponse({"destinations": suggestions[:limit]})


@csrf_exempt
def suggest_by_region(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    payload = _json_body(request)
    user_id = _get_user_id(request, payload)
    region_id = payload.get("region_id")
    limit = _clamp_limit(payload.get("limit"), default_limit=5, min_limit=1)

    if not user_id or not region_id:
        return JsonResponse({"scored_places": []})

    candidates = [
        {"id": f"{region_id}_place_{i}", "type": "place", "title": f"{region_id} place {i}"}
        for i in range(1, limit + 3)
    ]
    ranked = _rank_candidates(user_id, candidates)[:limit]
    scored_places = [
        {
            "place_id": entry["item"]["id"],
            "score": round(entry["score"], 3),
            "reasoning_tag": entry["reason_type"],
        }
        for entry in ranked
    ]
    return JsonResponse({"scored_places": scored_places})


@csrf_exempt
def record_interaction(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    payload = _json_body(request)
    user_id = _get_user_id(request, payload)
    item_id = payload.get("item_id")
    item_type = payload.get("item_type") or "place"
    interaction_type = payload.get("interaction") or payload.get("interaction_type") or "view"

    if not user_id or not item_id:
        return JsonResponse({"success": False}, status=400)

    UserInteraction.objects.create(
        interaction_id=f"int_{uuid.uuid4().hex[:12]}",
        user_id=user_id,
        item_id=item_id,
        item_type=item_type,
        interaction_type=interaction_type,
    )
    return JsonResponse({"success": True})


@csrf_exempt
def submit_feedback(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    payload = _json_body(request)
    user_id = _get_user_id(request, payload)
    recommendation_id = payload.get("recommendation_id")
    value = payload.get("value")

    if not user_id or not recommendation_id:
        return JsonResponse({"success": False}, status=400)

    rec = Recommendation.objects.filter(recommendation_id=recommendation_id, user_id=user_id).first()
    if rec is None:
        return JsonResponse({"success": False, "detail": "recommendation not found"}, status=404)

    parsed_value = int(value) if value is not None else 0
    rec.user_feedback = Recommendation.FEEDBACK_LIKE if parsed_value > 0 else Recommendation.FEEDBACK_DISLIKE
    rec.feedback_at = timezone.now()
    rec.save(update_fields=["user_feedback", "feedback_at"])

    Feedback.objects.create(
        feedback_id=f"fb_{uuid.uuid4().hex[:12]}",
        user_id=user_id,
        recommendation_id=recommendation_id,
        value=parsed_value,
    )
    return JsonResponse({"success": True})


def recommendation_reason(request, recommendation_id):
    rec = Recommendation.objects.filter(recommendation_id=recommendation_id).first()
    if not rec:
        return JsonResponse({"detail": "Not found"}, status=404)
    return JsonResponse(
        {
            "recommendation_id": rec.recommendation_id,
            "reason_type": rec.reason_type,
            "reason_description": rec.reason_description or "No explanation available.",
        }
    )


def list_user_recommendations(request, user_id):
    recs = Recommendation.objects.filter(user_id=user_id).order_by("-generated_at")[:50]
    items = [_recommendation_to_dto(rec) for rec in recs]
    return JsonResponse({"recommendations": items})
