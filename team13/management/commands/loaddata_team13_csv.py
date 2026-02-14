# بارگذاری داده‌های نمونه از temp_data/*.csv به دیتابیس team13 (SQLite)
import csv
import os
from uuid import UUID
from django.core.management.base import BaseCommand
from django.db import connections
from django.utils.dateparse import parse_datetime
from team13.models import (
    Place,
    PlaceTranslation,
    Event,
    EventTranslation,
    Image,
    Comment,
    HotelDetails,
    RestaurantDetails,
    MuseumDetails,
    PlaceAmenity,
    RouteLog,
)


def csv_path(filename):
    return os.path.join(os.path.dirname(__file__), "..", "..", "temp_data", filename)


class Command(BaseCommand):
    help = "Load sample data from team13/temp_data/*.csv into SQLite (team13 DB)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing team13 data before loading (optional).",
        )

    def handle(self, *args, **options):
        base = csv_path("")
        if not os.path.isdir(base):
            self.stderr.write(f"Folder not found: {base}")
            return

        if options.get("clear"):
            self.stdout.write("Clearing existing team13 data...")
            with connections["team13"].cursor() as cursor:
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
                        if "no such table" in str(e).lower():
                            pass
                        else:
                            raise
            self.stdout.write("Done clearing.")

        db = "team13"

        # 1) places
        path = csv_path("places.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
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
            self.stdout.write(f"Loaded places from {path}")

        # 2) place_translations
        path = csv_path("place_translations.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    place = Place.objects.using(db).get(place_id=UUID(row["place_id"]))
                    PlaceTranslation.objects.using(db).update_or_create(
                        place=place,
                        lang=row["lang"],
                        defaults={
                            "name": row.get("name", ""),
                            "description": row.get("description", ""),
                        },
                    )
            self.stdout.write(f"Loaded place_translations from {path}")

        # 3) events
        path = csv_path("events.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    Event.objects.using(db).get_or_create(
                        event_id=UUID(row["event_id"]),
                        defaults={
                            "start_at": parse_datetime(row["start_at"]),
                            "end_at": parse_datetime(row["end_at"]),
                            "city": row.get("city", ""),
                            "address": row.get("address", ""),
                            "latitude": float(row["latitude"]),
                            "longitude": float(row["longitude"]),
                        },
                    )
            self.stdout.write(f"Loaded events from {path}")

        # 4) event_translations
        path = csv_path("event_translations.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    event = Event.objects.using(db).get(event_id=UUID(row["event_id"]))
                    EventTranslation.objects.using(db).update_or_create(
                        event=event,
                        lang=row["lang"],
                        defaults={
                            "title": row.get("title", ""),
                            "description": row.get("description", ""),
                        },
                    )
            self.stdout.write(f"Loaded event_translations from {path}")

        # 5) images
        path = csv_path("images.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    Image.objects.using(db).get_or_create(
                        image_id=UUID(row["image_id"]),
                        defaults={
                            "target_type": row["target_type"],
                            "target_id": UUID(row["target_id"]),
                            "image_url": row["image_url"],
                        },
                    )
            self.stdout.write(f"Loaded images from {path}")

        # 6) comments
        path = csv_path("comments.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    obj, _ = Comment.objects.using(db).get_or_create(
                        comment_id=UUID(row["comment_id"]),
                        defaults={
                            "target_type": row["target_type"],
                            "target_id": UUID(row["target_id"]),
                            "rating": int(row["rating"]) if row.get("rating") else None,
                        },
                    )
                    Comment.objects.using(db).filter(pk=obj.pk).update(
                        created_at=parse_datetime(row["created_at"])
                    )
            self.stdout.write(f"Loaded comments from {path}")

        # 7) hotel_details
        path = csv_path("hotel_details.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    place = Place.objects.using(db).get(place_id=UUID(row["place_id"]))
                    HotelDetails.objects.using(db).update_or_create(
                        place=place,
                        defaults={
                            "stars": int(row["stars"]) if row.get("stars") else None,
                            "price_range": row.get("price_range", ""),
                        },
                    )
            self.stdout.write(f"Loaded hotel_details from {path}")

        # 8) restaurant_details
        path = csv_path("restaurant_details.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    place = Place.objects.using(db).get(place_id=UUID(row["place_id"]))
                    RestaurantDetails.objects.using(db).update_or_create(
                        place=place,
                        defaults={
                            "cuisine": row.get("cuisine", ""),
                            "avg_price": int(row["avg_price"]) if row.get("avg_price") else None,
                        },
                    )
            self.stdout.write(f"Loaded restaurant_details from {path}")

        # 9) museum_details
        path = csv_path("museum_details.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    place = Place.objects.using(db).get(place_id=UUID(row["place_id"]))
                    from datetime import time
                    open_at = row.get("open_at")
                    close_at = row.get("close_at")
                    if open_at and ":" in open_at:
                        h, m = open_at.strip().split(":")[:2]
                        open_at = time(int(h), int(m))
                    else:
                        open_at = None
                    if close_at and ":" in close_at:
                        h, m = close_at.strip().split(":")[:2]
                        close_at = time(int(h), int(m))
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
            self.stdout.write(f"Loaded museum_details from {path}")

        # 10) place_amenities
        path = csv_path("place_amenities.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    place = Place.objects.using(db).get(place_id=UUID(row["place_id"]))
                    PlaceAmenity.objects.using(db).get_or_create(
                        place=place,
                        amenity_name=row["amenity_name"],
                    )
            self.stdout.write(f"Loaded place_amenities from {path}")

        # 11) route_logs
        path = csv_path("route_logs.csv")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                r = csv.DictReader(f)
                for row in r:
                    src = Place.objects.using(db).get(place_id=UUID(row["source_place_id"]))
                    dst = Place.objects.using(db).get(place_id=UUID(row["destination_place_id"]))
                    obj = RouteLog.objects.using(db).create(
                        source_place=src,
                        destination_place=dst,
                        travel_mode=row["travel_mode"],
                        user_id=UUID(row["user_id"]) if row.get("user_id") else None,
                    )
                    RouteLog.objects.using(db).filter(pk=obj.pk).update(
                        created_at=parse_datetime(row["created_at"])
                    )
            self.stdout.write(f"Loaded route_logs from {path}")

        self.stdout.write(self.style.SUCCESS("Sample data load finished."))
