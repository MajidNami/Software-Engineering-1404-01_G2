import json
from uuid import UUID

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth import get_user_model

from core.auth import api_login_required
from .models import Team5RecommendationFeedback
from .services.contracts import DEFAULT_LIMIT
from .services.db_provider import DatabaseProvider
from .services.location_service import get_client_ip, resolve_client_city
from .services.recommendation_service import RecommendationService

TEAM_NAME = "team5"
FEEDBACK_ACTIONS = {"popular", "personalized", "nearest"}
User = get_user_model()
provider = DatabaseProvider()
recommendation_service = RecommendationService(provider)


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")


@require_GET
def get_cities(request):
    return JsonResponse(provider.get_cities(), safe=False)


@require_GET
def get_city_places(request, city_id: str):
    return JsonResponse(provider.get_city_places(city_id), safe=False)


@require_GET
def get_media(request):
    user_id = request.GET.get("userId")
    feed = recommendation_service.get_media_feed(user_id=user_id)
    return JsonResponse(feed)


@require_GET
def get_popular_recommendations(request):
    limit = _parse_limit(request)
    user_id = request.GET.get("userId")
    excluded_media_ids = _load_excluded_media_ids(user_id=user_id, action="popular")
    items = recommendation_service.get_popular(limit=limit, excluded_media_ids=excluded_media_ids)
    return JsonResponse(
        {
            "kind": "popular",
            "userId": user_id,
            "limit": limit,
            "count": len(items),
            "items": items,
        }
    )


@require_GET
def get_nearest_recommendations(request):
    limit = _parse_limit(request)
    user_id = request.GET.get("userId")
<<<<<<< Updated upstream
    excluded_media_ids = _load_excluded_media_ids(user_id=user_id, action="nearest")
=======
>>>>>>> Stashed changes
    city_override = request.GET.get("cityId")
    ip_override = request.GET.get("ip")

    client_ip = get_client_ip(request, ip_override=ip_override)
    resolved = resolve_client_city(
        cities=provider.get_cities(),
        client_ip=client_ip,
        preferred_city_id=city_override,
    )
    if not resolved:
        return JsonResponse(
            {
                "kind": "nearest",
                "source": "unresolved",
                "clientIp": client_ip,
                "detail": "Could not resolve user city from IP. Provide cityId query param for local testing.",
                "items": [],
                "count": 0,
                "limit": limit,
            },
            status=400,
        )

    city = resolved["city"]
    items = recommendation_service.get_nearest_by_city(
        city_id=city["cityId"],
        limit=limit,
<<<<<<< Updated upstream
        excluded_media_ids=excluded_media_ids,
=======
        user_id=user_id,
>>>>>>> Stashed changes
    )
    return JsonResponse(
        {
            "kind": "nearest",
            "title": "your nearest",
            "source": resolved["source"],
            "userId": user_id,
            "clientIp": client_ip,
            "cityId": city["cityId"],
            "cityName": city["cityName"],
            "limit": limit,
            "count": len(items),
            "items": items,
        }
    )


@require_GET
def get_personalized_recommendations(request):
    limit = _parse_limit(request)
    user_id = request.GET.get("userId")
    if not user_id and getattr(request.user, "is_authenticated", False):
        user_id = str(request.user.id)
    if not user_id:
        return JsonResponse({"detail": "userId query param is required"}, status=400)

    excluded_media_ids = _load_excluded_media_ids(user_id=user_id, action="personalized")
    items = recommendation_service.get_personalized(
        user_id=user_id,
        limit=limit,
        excluded_media_ids=excluded_media_ids,
    )
    similar_items = [item for item in items if item.get("matchReason") != "high_user_rating"]
    direct_items = [item for item in items if item.get("matchReason") == "high_user_rating"]
    source = "personalized"
    if not items:
        items = recommendation_service.get_popular(limit=limit, excluded_media_ids=excluded_media_ids)
        source = "fallback_popular"
        direct_items = items
        similar_items = []

    return JsonResponse(
        {
            "kind": "personalized",
            "source": source,
            "userId": user_id,
            "limit": limit,
            "count": len(items),
            "items": items,
            "highRatedItems": direct_items,
            "similarItems": similar_items,
        }
    )


@csrf_exempt
@require_POST
def submit_recommendation_feedback(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON body"}, status=400)

    user_id = payload.get("userId")
    action = str(payload.get("action") or "").strip().lower()
    liked = payload.get("liked")
    shown_media_ids = payload.get("shownMediaIds") or []

    user_uuid = _parse_uuid(user_id)
    if user_uuid is None:
        return JsonResponse({"detail": "Valid userId is required"}, status=400)
    if action not in FEEDBACK_ACTIONS:
        return JsonResponse({"detail": f"action must be one of {sorted(FEEDBACK_ACTIONS)}"}, status=400)
    if not isinstance(liked, bool):
        return JsonResponse({"detail": "liked must be a boolean"}, status=400)
    if not isinstance(shown_media_ids, list):
        return JsonResponse({"detail": "shownMediaIds must be a list"}, status=400)

    normalized_media_ids = []
    for media_id in shown_media_ids:
        text = str(media_id).strip()
        if text:
            normalized_media_ids.append(text)
    normalized_media_ids = list(dict.fromkeys(normalized_media_ids))

    Team5RecommendationFeedback.objects.create(
        user_id=user_uuid,
        action=action,
        liked=liked,
        shown_media_ids=normalized_media_ids,
    )
    return JsonResponse(
        {
            "ok": True,
            "userId": str(user_uuid),
            "action": action,
            "liked": liked,
            "storedMediaCount": len(normalized_media_ids),
            "detail": "Feedback saved",
        }
    )


@require_GET
def get_user_interests(request, user_id: str):
    interests = recommendation_service.get_user_interest_distribution(user_id=user_id)
    return JsonResponse(interests)


@require_GET
def get_registered_users(request):
    users = User.objects.filter(is_active=True).order_by("-date_joined")
    payload = [
        {
            "userId": str(user.id),
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "age": user.age,
            "dateJoined": user.date_joined.isoformat(),
        }
        for user in users
    ]
    return JsonResponse({"count": len(payload), "items": payload})


@require_GET
def get_user_ratings(request, user_id: str):
    ratings = recommendation_service.get_user_ratings(user_id=user_id)
    return JsonResponse({"userId": user_id, "count": len(ratings), "items": ratings})

<<<<<<< Updated upstream
=======
@require_POST
def train(request):
    trained = recommendation_service.train()
    return JsonResponse({"trained": bool(trained)})


@require_GET
def ml_status(request):
    return JsonResponse(recommendation_service.get_ml_status())

>>>>>>> Stashed changes

def _parse_limit(request) -> int:
    raw_limit = request.GET.get("limit")
    if raw_limit is None:
        return DEFAULT_LIMIT
    try:
        parsed = int(raw_limit)
    except ValueError:
        return DEFAULT_LIMIT
    return max(1, min(parsed, 100))


def _parse_uuid(value: str | None) -> UUID | None:
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return None


def _load_excluded_media_ids(*, user_id: str | None, action: str) -> set[str]:
    user_uuid = _parse_uuid(user_id)
    if user_uuid is None:
        return set()

    latest = (
        Team5RecommendationFeedback.objects.filter(user_id=user_uuid, action=action)
        .order_by("-created_at", "-id")
        .first()
    )
    if latest is None or latest.liked:
        return set()

    output: set[str] = set()
    for media_id in latest.shown_media_ids or []:
        text = str(media_id).strip()
        if text:
            output.add(text)
    return output