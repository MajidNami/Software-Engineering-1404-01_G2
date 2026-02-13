import requests
from django.conf import settings
from .models import Place
from .ai_service import generate_ai_metadata_for_place

CORE_URL = getattr(settings, 'CORE_BASE_URL', 'http://core:8000')

def fetch_wiki_data(place_id):
    try:
        url = f"{CORE_URL}/api/wiki/content?place={place_id}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("summary", ""), data.get("tags", [])
    except: pass
    return "", []

def get_or_enrich_places(candidate_place_ids):
    existing_places = Place.objects.filter(place_id__in=candidate_place_ids)
    existing_ids = set(p.place_id for p in existing_places)

    missing_ids = set(candidate_place_ids) - existing_ids
    new_places = []

    for pid in missing_ids:
        summary, tags = fetch_wiki_data(pid)
        ai_data = generate_ai_metadata_for_place(pid, summary, tags)

        try:
            safe_duration = int(ai_data.get("duration", 2))
        except (ValueError, TypeError):
            safe_duration = 2

        new_place = Place(
            place_id=pid,
            place_name=pid.replace("-", " ").title(),
            region_id=ai_data.get("region_id", "unknown"),
            region_name=ai_data.get("region_name", "نامشخص"),
            budget_level=ai_data.get("budget_level", "MODERATE"),
            travel_style=ai_data.get("travel_style", "FAMILY"),
            duration=safe_duration,
            season=ai_data.get("season", "SPRING"),
            ai_reason=ai_data.get("ai_reason", "")
        )
        new_places.append(new_place)

    if new_places:
        Place.objects.bulk_create(new_places)

    return Place.objects.filter(place_id__in=candidate_place_ids)