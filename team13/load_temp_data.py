#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Read data from team13/temp_data_inseart (JSON) and insert into team13 SQLite.
No CSV storage; data is loaded from JSON and saved in the correct format in SQLite.

Run from project root:
  py -3.11 team13/load_temp_data.py [--clear] [--path path/to/folder]

Default data folder: team13/temp_data_inseart (hotels.json, hospitals.json, restaurants.json).
"""

import json
import os
import sys
import uuid

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app404.settings")
    import django
    django.setup()

# Namespace for deterministic place_id from hotel_id / hospital / restaurant key
NAMESPACE_HOTEL = uuid.uuid5(uuid.NAMESPACE_URL, "https://team13/place/hotel")
NAMESPACE_HOSPITAL = uuid.uuid5(uuid.NAMESPACE_URL, "https://team13/place/hospital")
NAMESPACE_RESTAURANT = uuid.uuid5(uuid.NAMESPACE_URL, "https://team13/place/restaurant")
NAMESPACE_SIRJAN = uuid.uuid5(uuid.NAMESPACE_URL, "https://team13/place/sirjan_default")


def get_data_dir():
    """Prefer team13/temp_data_inseart, then project root temp_data_inseart, then team13/temp_data."""
    team13_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(team13_dir)
    for base, names in [
        (team13_dir, ("temp_data_inseart", "temp_data_insert", "temp_data")),
        (project_root, ("temp_data_inseart", "temp_data_insert", "temp_data")),
    ]:
        for name in names:
            path = os.path.join(base, name)
            if os.path.isdir(path):
                return path
    return os.path.join(team13_dir, "temp_data_inseart")


def _clear_team13(db):
    from django.db import connections
    with connections[db].cursor() as cursor:
        for table in [
            "team13_route_logs",
            "team13_place_amenities",
            "team13_museum_details",
            "team13_restaurant_details",
            "team13_hotel_details",
            "team13_comments",
            "team13_images",
            "team13_event_translations",
            "team13_events",
            "team13_place_translations",
            "team13_places",
        ]:
            try:
                cursor.execute(f"DELETE FROM {table}")
            except Exception as e:
                if "no such table" not in str(e).lower():
                    raise


def load_from_json(data_dir, db="team13", clear=False):
    """
    Load hotels.json from data_dir (e.g. team13/temp_data_inseart)
    into team13 SQLite in the correct schema (Place, PlaceTranslation, HotelDetails).
    """
    from team13.models import HotelDetails, Place, PlaceTranslation

    hotels_path = os.path.join(data_dir, "hotels.json")
    if not os.path.isfile(hotels_path):
        print(f"hotels.json not found in {data_dir}")
        return False

    if clear:
        print("Clearing existing team13 data...")
        _clear_team13(db)
        print("Done clearing.")

    with open(hotels_path, "r", encoding="utf-8") as f:
        hotels = json.load(f)

    if not isinstance(hotels, list):
        print("hotels.json must be a JSON array.")
        return False

    created = 0
    for h in hotels:
        hotel_id = h.get("hotel_id")
        if hotel_id is None:
            continue
        loc = h.get("location") or {}
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        if lat is None or lng is None:
            continue
        # Deterministic UUID so re-run does not duplicate
        place_id = uuid.uuid5(NAMESPACE_HOTEL, str(hotel_id))
        city = (h.get("city_name_fa") or h.get("city") or "").strip()
        address = (h.get("address") or "").strip()
        name_fa = (h.get("name_fa") or "").strip() or "هتل"
        name_en = (h.get("name_en") or "").strip() or "Hotel"
        desc_fa = (h.get("description_fa") or "").strip()
        desc_en = (h.get("description_en") or "").strip()
        stars = h.get("stars")
        if stars is not None:
            try:
                stars = int(stars)
            except (TypeError, ValueError):
                stars = None
        price_tier = (h.get("price_tier") or "").strip()
        price_range = price_tier or ""

        place, place_created = Place.objects.using(db).get_or_create(
            place_id=place_id,
            defaults={
                "type": "hotel",
                "city": city[:255],
                "address": address,
                "latitude": float(lat),
                "longitude": float(lng),
            },
        )
        if place_created:
            created += 1
        else:
            Place.objects.using(db).filter(place_id=place_id).update(
                city=city[:255], address=address, latitude=float(lat), longitude=float(lng)
            )

        PlaceTranslation.objects.using(db).update_or_create(
            place=place,
            lang="fa",
            defaults={"name": name_fa[:255], "description": desc_fa},
        )
        PlaceTranslation.objects.using(db).update_or_create(
            place=place,
            lang="en",
            defaults={"name": name_en[:255], "description": desc_en},
        )
        HotelDetails.objects.using(db).update_or_create(
            place=place,
            defaults={"stars": stars, "price_range": price_range[:64]},
        )

        # Optional: amenities (IDs in JSON; map to names for team13_place_amenities)
        amenity_names = {
            1: "پارکینگ",
            2: "وای‌فای",
            3: "استخر",
            4: "سالن ورزش",
            5: "رستوران",
            6: "کافی‌شاپ",
            7: "اینترنت",
            8: "تهویه",
            9: "صبحانه",
            10: "استقبال ۲۴ ساعته",
            11: "صبحانه",
        }
        amenity_ids = h.get("amenities") or []
        if isinstance(amenity_ids, list):
            from team13.models import PlaceAmenity
            for aid in amenity_ids:
                aname = amenity_names.get(aid) or f"amenity_{aid}"
                PlaceAmenity.objects.using(db).get_or_create(
                    place=place,
                    amenity_name=aname[:128],
                )

    print(f"Loaded {len(hotels)} hotels from {hotels_path} (created {created} new places).")
    return True


def load_hospitals_from_json(data_dir, db="team13"):
    """
    Load hospitals.json from data_dir into team13 SQLite (Place type=hospital + PlaceTranslation).
    Uses deterministic UUID from name_fa+lat+lng so re-run does not duplicate. No CSV; JSON only.
    """
    from team13.models import Place, PlaceTranslation

    hospitals_path = os.path.join(data_dir, "hospitals.json")
    if not os.path.isfile(hospitals_path):
        print(f"hospitals.json not found in {data_dir}")
        return False

    with open(hospitals_path, "r", encoding="utf-8") as f:
        hospitals = json.load(f)

    if not isinstance(hospitals, list):
        print("hospitals.json must be a JSON array.")
        return False

    created = 0
    for h in hospitals:
        loc = h.get("location") or {}
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        if lat is None or lng is None:
            continue
        name_fa = (h.get("name_fa") or "").strip() or "بیمارستان"
        name_en = (h.get("name_en") or "").strip() or "Hospital"
        city = (h.get("city_name_fa") or h.get("city") or "").strip()[:255]
        address = (h.get("address") or "").strip()
        desc_fa = (h.get("description_fa") or "").strip()
        desc_en = (h.get("description_en") or "").strip()
        # Deterministic UUID so re-run does not duplicate
        key = f"{name_fa}|{float(lat)}|{float(lng)}"
        place_id = uuid.uuid5(NAMESPACE_HOSPITAL, key)

        place, place_created = Place.objects.using(db).get_or_create(
            place_id=place_id,
            defaults={
                "type": Place.PlaceType.HOSPITAL,
                "city": city,
                "address": address,
                "latitude": float(lat),
                "longitude": float(lng),
            },
        )
        if place_created:
            created += 1
        else:
            Place.objects.using(db).filter(place_id=place_id).update(
                city=city, address=address, latitude=float(lat), longitude=float(lng)
            )

        PlaceTranslation.objects.using(db).update_or_create(
            place=place,
            lang="fa",
            defaults={"name": name_fa[:255], "description": desc_fa},
        )
        PlaceTranslation.objects.using(db).update_or_create(
            place=place,
            lang="en",
            defaults={"name": name_en[:255], "description": desc_en},
        )

    print(f"Loaded {len(hospitals)} hospitals from {hospitals_path} (created {created} new places).")
    return True


def load_restaurants_from_json(data_dir, db="team13"):
    """
    Load restaurants.json from data_dir into team13 SQLite (Place type=food + PlaceTranslation + RestaurantDetails).
    Uses deterministic UUID from restaurant id so re-run does not duplicate. No CSV; JSON only.
    """
    from team13.models import Place, PlaceTranslation, RestaurantDetails

    restaurants_path = os.path.join(data_dir, "restaurants.json")
    if not os.path.isfile(restaurants_path):
        print(f"restaurants.json not found in {data_dir}")
        return False

    with open(restaurants_path, "r", encoding="utf-8") as f:
        restaurants = json.load(f)

    if not isinstance(restaurants, list):
        print("restaurants.json must be a JSON array.")
        return False

    # Map price_tier to optional avg_price (تومان تقریبی) or leave None
    price_tier_to_price = {"expensive": 150000, "moderate": 70000, "low": 30000}

    created = 0
    for r in restaurants:
        rid = r.get("id")
        if rid is None:
            continue
        loc = r.get("location") or {}
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        if lat is None or lng is None:
            continue
        name_fa = (r.get("name_fa") or "").strip() or "رستوران"
        name_en = (r.get("name_en") or "").strip() or "Restaurant"
        city = (r.get("city_name_fa") or r.get("city") or "").strip()[:255]
        address = (r.get("address") or "").strip()
        desc_fa = (r.get("description_fa") or "").strip()
        desc_en = (r.get("description_en") or "").strip()
        price_tier = (r.get("price_tier") or "").strip().lower()
        avg_price = price_tier_to_price.get(price_tier) if price_tier else None

        place_id = uuid.uuid5(NAMESPACE_RESTAURANT, str(rid))
        place, place_created = Place.objects.using(db).get_or_create(
            place_id=place_id,
            defaults={
                "type": Place.PlaceType.FOOD,
                "city": city,
                "address": address,
                "latitude": float(lat),
                "longitude": float(lng),
            },
        )
        if place_created:
            created += 1
        else:
            Place.objects.using(db).filter(place_id=place_id).update(
                city=city, address=address, latitude=float(lat), longitude=float(lng)
            )

        PlaceTranslation.objects.using(db).update_or_create(
            place=place,
            lang="fa",
            defaults={"name": name_fa[:255], "description": desc_fa},
        )
        PlaceTranslation.objects.using(db).update_or_create(
            place=place,
            lang="en",
            defaults={"name": name_en[:255], "description": desc_en},
        )
        RestaurantDetails.objects.using(db).update_or_create(
            place=place,
            defaults={"cuisine": "", "avg_price": avg_price},
        )

    print(f"Loaded {len(restaurants)} restaurants from {restaurants_path} (created {created} new places).")
    return True


def load_sirjan_defaults(db="team13"):
    """
    Add default hospitals, clinics and fire stations in Sirjan (Kerman province).
    Uses get_or_create so safe to run multiple times.
    """
    from team13.models import Place, PlaceTranslation

    # Sirjan center approx: 29.4510, 55.6809
    city = "سیرجان"
    city_en = "Sirjan"
    defaults = [
        # type, name_fa, name_en, lat, lng, address_fa
        ("hospital", "بیمارستان امام خمینی سیرجان", "Imam Khomeini Hospital Sirjan", 29.4520, 55.6820, "بلوار امام خمینی، سیرجان"),
        ("hospital", "بیمارستان شهید بهشتی سیرجان", "Shahid Beheshti Hospital Sirjan", 29.4485, 55.6780, "خیابان شهید بهشتی، سیرجان"),
        ("hospital", "بیمارستان ولیعصر سیرجان", "Valiasr Hospital Sirjan", 29.4550, 55.6750, "جاده ولیعصر، سیرجان"),
        ("clinic", "کلینیک تخصصی سیرجان", "Sirjan Specialized Clinic", 29.4500, 55.6850, "خیابان مطهری، سیرجان"),
        ("clinic", "کلینیک شبانه‌روزی سیرجان", "Sirjan 24h Clinic", 29.4470, 55.6820, "بلوار آزادی، سیرجان"),
        ("clinic", "کلینیک پارسیان سیرجان", "Parsian Clinic Sirjan", 29.4530, 55.6770, "خیابان پارسیان، سیرجان"),
        ("fire_station", "ایستگاه آتش‌نشانی مرکزی سیرجان", "Sirjan Central Fire Station", 29.4515, 55.6810, "بلوار جمهوری، سیرجان"),
        ("fire_station", "ایستگاه آتش‌نشانی شماره ۲ سیرجان", "Sirjan Fire Station No.2", 29.4490, 55.6740, "جاده قدیم، سیرجان"),
    ]
    created = 0
    for i, (ptype, name_fa, name_en, lat, lng, address_fa) in enumerate(defaults):
        place_id = uuid.uuid5(NAMESPACE_SIRJAN, f"sirjan-{ptype}-{i}")
        place, place_created = Place.objects.using(db).get_or_create(
            place_id=place_id,
            defaults={
                "type": ptype,
                "city": city,
                "address": address_fa,
                "latitude": lat,
                "longitude": lng,
            },
        )
        if place_created:
            created += 1
        PlaceTranslation.objects.using(db).update_or_create(
            place=place,
            lang="fa",
            defaults={"name": name_fa, "description": ""},
        )
        PlaceTranslation.objects.using(db).update_or_create(
            place=place,
            lang="en",
            defaults={"name": name_en, "description": ""},
        )
    print(f"Sirjan defaults: {len(defaults)} places (created {created} new).")
    return True


def run_load(clear=False, data_dir=None):
    data_dir = data_dir or get_data_dir()
    if not os.path.isdir(data_dir):
        print(f"Data folder not found: {data_dir}")
        print("Put hotels.json (and optionally hospitals.json, restaurants.json) in team13/temp_data_inseart or pass --path.")
        return False

    ok = False
    # Prefer JSON load (hotels.json)
    if os.path.isfile(os.path.join(data_dir, "hotels.json")):
        ok = load_from_json(data_dir, db="team13", clear=clear)
    if not ok and _has_any_csv(data_dir):
        ok = _run_load_csv(data_dir, clear=clear)

    # Load hospitals.json if present (additive; no clear)
    if os.path.isfile(os.path.join(data_dir, "hospitals.json")):
        load_hospitals_from_json(data_dir, db="team13")
        ok = True

    # Load restaurants.json if present (additive; no clear)
    if os.path.isfile(os.path.join(data_dir, "restaurants.json")):
        load_restaurants_from_json(data_dir, db="team13")
        ok = True

    # Always ensure Sirjan default places (hospitals, clinics, fire stations)
    load_sirjan_defaults(db="team13")
    return ok


def _has_any_csv(data_dir):
    return os.path.isfile(os.path.join(data_dir, "places.csv"))


def _run_load_csv(data_dir, clear=False):
    """Legacy: load from CSV files in data_dir (e.g. team13/temp_data or team13/temp_data_inseart)."""
    import csv
    from datetime import time
    from uuid import UUID

    from django.db import connections
    from django.utils.dateparse import parse_datetime

    from team13.models import (
        Comment,
        Event,
        EventTranslation,
        HotelDetails,
        Image,
        MuseumDetails,
        Place,
        PlaceAmenity,
        PlaceTranslation,
        RestaurantDetails,
        RouteLog,
    )

    def csv_path(filename):
        return os.path.join(data_dir, filename)

    def _parse_dt(value):
        from django.conf import settings
        from django.utils import timezone
        dt = parse_datetime(value)
        if dt and timezone.is_naive(dt) and settings.USE_TZ:
            dt = timezone.make_aware(dt)
        return dt

    db = "team13"
    if clear:
        print("Clearing existing team13 data...")
        _clear_team13(db)
        print("Done clearing.")

    # 1) places
    path = csv_path("places.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                Place.objects.using(db).get_or_create(
                    place_id=UUID(row["place_id"]),
                    defaults={
                        "type": row["type"],
                        "city": row.get("city", ""),
                        "address": row.get("address", ""),
                        "latitude": float(row["latitude"]),
                        "longitude": float(row["longitude"]),
                    },
                )
        print(f"Loaded places from {path}")

    # 2) place_translations
    path = csv_path("place_translations.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                place = Place.objects.using(db).get(place_id=UUID(row["place_id"]))
                PlaceTranslation.objects.using(db).update_or_create(
                    place=place,
                    lang=row["lang"],
                    defaults={"name": row.get("name", ""), "description": row.get("description", "")},
                )
        print(f"Loaded place_translations from {path}")

    # 3) events
    path = csv_path("events.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                Event.objects.using(db).get_or_create(
                    event_id=UUID(row["event_id"]),
                    defaults={
                        "start_at": _parse_dt(row["start_at"]),
                        "end_at": _parse_dt(row["end_at"]),
                        "city": row.get("city", ""),
                        "address": row.get("address", ""),
                        "latitude": float(row["latitude"]),
                        "longitude": float(row["longitude"]),
                    },
                )
        print(f"Loaded events from {path}")

    # 4) event_translations
    path = csv_path("event_translations.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                event = Event.objects.using(db).get(event_id=UUID(row["event_id"]))
                EventTranslation.objects.using(db).update_or_create(
                    event=event,
                    lang=row["lang"],
                    defaults={"title": row.get("title", ""), "description": row.get("description", "")},
                )
        print(f"Loaded event_translations from {path}")

    # 5) images
    path = csv_path("images.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                Image.objects.using(db).get_or_create(
                    image_id=UUID(row["image_id"]),
                    defaults={
                        "target_type": row["target_type"],
                        "target_id": UUID(row["target_id"]),
                        "image_url": row["image_url"],
                    },
                )
        print(f"Loaded images from {path}")

    # 6) comments
    path = csv_path("comments.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                obj, _ = Comment.objects.using(db).get_or_create(
                    comment_id=UUID(row["comment_id"]),
                    defaults={
                        "target_type": row["target_type"],
                        "target_id": UUID(row["target_id"]),
                        "rating": int(row["rating"]) if row.get("rating") else None,
                    },
                )
                Comment.objects.using(db).filter(pk=obj.pk).update(created_at=_parse_dt(row["created_at"]))
        print(f"Loaded comments from {path}")

    # 7) hotel_details
    path = csv_path("hotel_details.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                place = Place.objects.using(db).get(place_id=UUID(row["place_id"]))
                HotelDetails.objects.using(db).update_or_create(
                    place=place,
                    defaults={
                        "stars": int(row["stars"]) if row.get("stars") else None,
                        "price_range": row.get("price_range", ""),
                    },
                )
        print(f"Loaded hotel_details from {path}")

    # 8) restaurant_details
    path = csv_path("restaurant_details.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                place = Place.objects.using(db).get(place_id=UUID(row["place_id"]))
                RestaurantDetails.objects.using(db).update_or_create(
                    place=place,
                    defaults={
                        "cuisine": row.get("cuisine", ""),
                        "avg_price": int(row["avg_price"]) if row.get("avg_price") else None,
                    },
                )
        print(f"Loaded restaurant_details from {path}")

    # 9) museum_details
    path = csv_path("museum_details.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                place = Place.objects.using(db).get(place_id=UUID(row["place_id"]))
                open_at = row.get("open_at")
                close_at = row.get("close_at")
                if open_at and ":" in open_at:
                    parts = open_at.strip().split(":")
                    open_at = time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
                else:
                    open_at = None
                if close_at and ":" in close_at:
                    parts = close_at.strip().split(":")
                    close_at = time(int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
                else:
                    close_at = None
                MuseumDetails.objects.using(db).update_or_create(
                    place=place,
                    defaults={
                        "open_at": open_at,
                        "close_at": close_at,
                        "ticket_price": int(row["ticket_price"]) if row.get("ticket_price") else None,
                    },
                )
        print(f"Loaded museum_details from {path}")

    # 10) place_amenities
    path = csv_path("place_amenities.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                place = Place.objects.using(db).get(place_id=UUID(row["place_id"]))
                PlaceAmenity.objects.using(db).get_or_create(
                    place=place,
                    amenity_name=row["amenity_name"],
                )
        print(f"Loaded place_amenities from {path}")

    # 11) route_logs
    path = csv_path("route_logs.csv")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                src = Place.objects.using(db).get(place_id=UUID(row["source_place_id"]))
                dst = Place.objects.using(db).get(place_id=UUID(row["destination_place_id"]))
                obj = RouteLog.objects.using(db).create(
                    source_place=src,
                    destination_place=dst,
                    travel_mode=row["travel_mode"],
                    user_id=UUID(row["user_id"]) if row.get("user_id") else None,
                )
                RouteLog.objects.using(db).filter(pk=obj.pk).update(
                    created_at=_parse_dt(row["created_at"])
                )
        print(f"Loaded route_logs from {path}")

    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Load data from team13/temp_data_inseart (JSON) into team13 SQLite")
    parser.add_argument("--clear", action="store_true", help="Clear existing team13 data before load")
    parser.add_argument("--path", type=str, default=None, help="Path to data folder (default: team13/temp_data_inseart)")
    args = parser.parse_args()
    ok = run_load(clear=args.clear, data_dir=args.path)
    if ok:
        print("Data load finished successfully.")
    else:
        sys.exit(1)
