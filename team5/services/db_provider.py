"""Database-backed provider for Team5 recommendation data."""

from django.db.models import Avg, Count

from team5.models import Team5City, Team5Media, Team5MediaRating, Team5Place

from .contracts import CityRecord, MediaRecord, PlaceRecord
from .data_provider import DataProvider


class DatabaseProvider(DataProvider):
    def get_cities(self) -> list[CityRecord]:
        rows = Team5City.objects.all().order_by("city_name")
        return [
            {
                "cityId": row.city_id,
                "cityName": row.city_name,
                "coordinates": [row.latitude, row.longitude],
            }
            for row in rows
        ]

    def get_city_places(self, city_id: str) -> list[PlaceRecord]:
        rows = Team5Place.objects.filter(city_id=city_id).order_by("place_name")
        return [self._place_to_record(row) for row in rows]

    def get_all_places(self) -> list[PlaceRecord]:
        rows = Team5Place.objects.select_related("city").all().order_by("place_name")
        return [self._place_to_record(row) for row in rows]

    def get_media(self) -> list[MediaRecord]:
        stats = (
            Team5MediaRating.objects.values("media_id")
            .annotate(avg_rate=Avg("rate"), count_rate=Count("id"))
            .order_by()
        )
        stats_by_media = {
            row["media_id"]: {
                "overallRate": round(float(row["avg_rate"]), 2),
                "ratingsCount": int(row["count_rate"]),
            }
            for row in stats
        }

        rows = Team5Media.objects.select_related("place").all().order_by("media_id")
        output: list[MediaRecord] = []
        for row in rows:
            item_stats = stats_by_media.get(row.media_id, {"overallRate": 0.0, "ratingsCount": 0})
            output.append(
                {
                    "mediaId": row.media_id,
                    "placeId": row.place_id,
                    "title": row.title,
                    "caption": row.caption,
                    "overallRate": item_stats["overallRate"],
                    "ratingsCount": item_stats["ratingsCount"],
                    "userRatings": [],
                }
            )
        return output

    def _place_to_record(self, place: Team5Place) -> PlaceRecord:
        return {
            "placeId": place.place_id,
            "cityId": place.city_id,
            "placeName": place.place_name,
            "coordinates": [place.latitude, place.longitude],
        }
