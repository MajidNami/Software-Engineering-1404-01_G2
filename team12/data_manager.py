import requests
import json
from django.conf import settings
from .models import Place, Region
from .ai_service import generate_ai_metadata_for_place

CORE_URL = getattr(settings, 'CORE_BASE_URL', 'http://core:8000')

# Mock data for other teams' services (Wiki, Engagement, Facilities)
MOCK_WIKI_DATA = {
    "tehran milad tower": {
        "summary": "برج میلاد بلندترین آسمان‌خراش ایران و ششمین برج مخابراتی بلند جهان است.",
        "tags": ["برج", "تهران", "مدرن", "تفریحی"],
        "category": "جاذبه شهری"
    },
    "isfahan si o se pol": {
        "summary": "سی و سه پل یکی از شاهکارهای معماری صفوی و از مشهورترین پل‌های تاریخی ایران است.",
        "tags": ["تاریخی", "پل", "اصفهان"],
        "category": "جاذبه تاریخی"
    }
}

MOCK_ENGAGEMENT_DATA = {
    "tehran-milad-tower": {"ratingSummary": {"avg": 4.5}},
    "isfahan-si-o-se-pol": {"ratingSummary": {"avg": 4.8}}
}

MOCK_FACILITIES_DATA = {
    "results": [
        {"id": 1, "name": "Laleh Hotel", "type": "HOTEL", "lat": 35.79, "lng": 51.38},
        {"id": 2, "name": "Nayeb Restaurant", "type": "RESTAURANT", "lat": 35.74, "lng": 51.37}
    ]
}

# Mock data for Team 12's own endpoints (as per team12.yaml)
MOCK_REGIONS_LIST = [
    {
        "region_id": "tehran",
        "region_name": "تهران",
        "match_score": 0.95,
        "cover_image": "http://localhost:8000/static/images/tehran.jpg",
        "ai_reason": "پایتختی با ترکیبی از مدرنیته و تاریخ، مناسب برای سفرهای خانوادگی در بهار."
    },
    {
        "region_id": "isfahan",
        "region_name": "اصفهان",
        "match_score": 0.88,
        "cover_image": "http://localhost:8000/static/images/isfahan.jpg",
        "ai_reason": "شهر گنبدهای فیروزه‌ای، ایده‌آل برای علاقه‌مندان به معماری و هنر."
    }
]


def fetch_wiki_data(place_name):
    try:
        url = f"{CORE_URL}/api/wiki/content?place={place_name}"
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            print(f"DEBUG: Fetched real Wiki data for {place_name}")
            data = resp.json()
            return data.get("summary"), data.get("tags", []), data.get("category", "")
    except Exception as e:
        print(f"DEBUG: Wiki API failed, using Mock. Error: {str(e)}")

    mock_key = place_name.lower()
    data = MOCK_WIKI_DATA.get(mock_key, {
        "summary": "یک جاذبه گردشگری زیبا در ایران.",
        "tags": ["گردشگری", "ایران"],
        "category": "عمومی"
    })
    return data["summary"], data["tags"], data["category"]



def fetch_engagement_data(place_id):
    try:
        url = f"{CORE_URL}/api/v1/engagement?entityType=place&entityId={place_id}&commentLimit=0&includeMedia=false"
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            print(f"DEBUG: Fetched real Engagement data for {place_id}")
            summary = resp.json().get("ratingSummary", {})
            return float(summary.get("avg", 0.0))
    except Exception as e:
        print(f"DEBUG: Engagement API failed, using Mock. Error: {str(e)}")

    mock_data = MOCK_ENGAGEMENT_DATA.get(place_id, {"ratingSummary": {"avg": 3.8}})
    return float(mock_data["ratingSummary"]["avg"])


def get_suggested_regions():
    # Use database if exists, else use Mock
    regions = Region.objects.all()
    if regions.exists():
        destinations = []
        for r in regions:
            destinations.append({
                "region_id": r.region_id,
                "region_name": r.region_name,
                "match_score": 0.85,
                "cover_image": f"http://localhost:8000/static/images/{r.region_id}.jpg",
                "ai_reason": f"منطقه‌ای جذاب در {r.region_name} که با سلیقه شما سازگار است."
            })
        return destinations
    return MOCK_REGIONS_LIST


def get_places_by_region(region_id):
    # Filter places by region_id
    places = Place.objects.filter(region__region_id=region_id)
    if places.exists():
        scored_places = []
        for p in places:
            scored_places.append({
                "place_id": p.place_id,
                "score": 0.9,
                "ai_reason": p.ai_reason or "مکان پیشنهادی بر اساس تحلیل هوش مصنوعی."
            })
        return scored_places

    # Return Mock if no data in DB for this region
    return [
        {"place_id": f"{region_id}-attraction-1", "score": 0.92, "ai_reason": "جاذبه برتر این منطقه."},
        {"place_id": f"{region_id}-attraction-2", "score": 0.85, "ai_reason": "مکانی دیدنی با امتیاز بالا."}
    ]


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
            safe_duration = int(ai_data.get("duration", 2) or 2)
        except:
            safe_duration = 2

        r_id = ai_data.get("region_id") or "unknown"
        r_name = ai_data.get("region_name") or "نامشخص"

        region_obj, created = Region.objects.get_or_create(
            region_id=r_id,
            defaults={'region_name': r_name}
        )

        new_place = Place(
            place_id=pid,
            place_name=place_name,
            region=region_obj,
            budget_level=(ai_data.get("budget_level") or "MODERATE").upper(),
            travel_style=(ai_data.get("travel_style") or "FAMILY").upper(),
            duration=safe_duration,
            season=(ai_data.get("season") or "SPRING").upper().replace("AUTUMN", "FALL"),
            base_rate=base_rate,
            ai_reason=ai_data.get("ai_reason") or "مقصدی جذاب برای سفر."
        )
        new_places.append(new_place)

    if new_places:
        Place.objects.bulk_create(new_places)

    return list(existing_places) + new_places