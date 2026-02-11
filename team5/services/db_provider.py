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
<<<<<<< Updated upstream
=======
    
    def get_all_media_ratings(self) -> list[UserMediaRatingRecord]:
        rows = Team5MediaRating.objects.all()

        output: list[UserMediaRatingRecord] = []
        for row in rows:
            output.append(
                {
                    "userId": str(row.user_id),
                    "mediaId": row.media_id,
                    "rate": float(row.rate),
                }
            )
        return output
    
    def get_all_place_ratings(self) -> list[UserPlaceRatingRecord]:
        media_map = {
            m.media_id: {
                "place_id": m.place_id,
                "title": m.title,
            }
            for m in Team5Media.objects.select_related("place").all()
        }
        ratings = Team5MediaRating.objects.all()
        text_sentiment = TextSentiment()

        output = []
        for r in ratings:
            media = media_map.get(r.media_id)
            if media is None:
                continue  # skip invalid ratings if any

            media_place_rate = text_sentiment.sentiment(media["title"])
            user_media_rate = r.rate - 2.5
            user_place_rate = 2.5 + user_media_rate * media_place_rate

            output.append({
                "userId": str(r.user_id),
                "placeId": media["place_id"],
                "rate": float(user_place_rate),
            })

        return output

>>>>>>> Stashed changes

    def _place_to_record(self, place: Team5Place) -> PlaceRecord:
        return {
            "placeId": place.place_id,
            "cityId": place.city_id,
            "placeName": place.place_name,
            "coordinates": [place.latitude, place.longitude],
        }
