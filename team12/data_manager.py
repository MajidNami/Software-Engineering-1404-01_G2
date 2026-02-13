import requests
from django.conf import settings
from .models import Place, Region
from .ai_service import generate_ai_metadata_for_place

CORE_URL = getattr(settings, 'CORE_BASE_URL', 'http://core:8000')

def fetch_wiki_data(place_name):
    try:
        url = f"{CORE_URL}/api/wiki/content?place={place_name}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("summary", ""), data.get("tags", []), data.get("category", "")
    except:
        pass
    return "", [], ""

def fetch_engagement_data(place_id):
    try:
        url = f"{CORE_URL}/api/v1/engagement?entityType=place&entityId={place_id}&commentLimit=0&includeMedia=false"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            summary = resp.json().get("ratingSummary", {})
            if summary:
                return float(summary.get("avg", 0.0))
    except:
        pass
    return 3.0

def fetch_nearby_facilities(lat, lng, radius=10000):
    try:
        url = f"{CORE_URL}/team4/api/facilities/nearby/?lat={lat}&lng={lng}&radius={radius}"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            return resp.json().get("results", [])
    except:
        pass
    return []

def get_or_enrich_places(candidate_place_ids):
    existing_places = Place.objects.filter(place_id__in=candidate_place_ids)
    existing_ids = set(p.place_id for p in existing_places)
    missing_ids = set(candidate_place_ids) - existing_ids
    new_places = []

    for pid in missing_ids:
        place_name = pid.replace("-", " ").title()
        summary, tags, category = fetch_wiki_data(place_name)
        base_rate = fetch_engagement_data(pid)
        ai_data = generate_ai_metadata_for_place(pid, summary, tags)

        try:
            safe_duration = int(ai_data.get("duration", 2))
        except (ValueError, TypeError):
            safe_duration = 2

        r_id = ai_data.get("region_id", "unknown")
        r_name = ai_data.get("region_name", "نامشخص")

        region_obj, created = Region.objects.get_or_create(
            region_id=r_id,
            defaults={'region_name': r_name}
        )

        new_place = Place(
            place_id=pid,
            place_name=place_name,
            region=region_obj,
            budget_level=ai_data.get("budget_level", "MODERATE").upper(),
            travel_style=ai_data.get("travel_style", "FAMILY").upper(),
            duration=safe_duration,
            season=ai_data.get("season", "SPRING").upper(),
            base_rate=base_rate,
            ai_reason=ai_data.get("ai_reason", "")
        )
        new_places.append(new_place)

    if new_places:
        Place.objects.bulk_create(new_places)

    return list(existing_places) + new_places