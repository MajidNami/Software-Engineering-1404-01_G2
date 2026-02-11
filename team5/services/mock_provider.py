"""Mock data provider backed by JSON files."""

import json
from functools import lru_cache
from pathlib import Path

from .contracts import CityRecord, MediaRecord, PlaceRecord, UserMediaRatingRecord, UserPlaceRatingRecord
from .data_provider import DataProvider


class MockProvider(DataProvider):
    def __init__(self, base_path: Path | None = None):
        if base_path is None:
            self.base_path = Path(__file__).resolve().parent.parent / "mock_data"
        else:
            self.base_path = base_path

    def get_cities(self) -> list[CityRecord]:
        return list(_read_json(self.base_path / "cities.json"))

    def get_city_places(self, city_id: str) -> list[PlaceRecord]:
        places = self.get_all_places()
        return [place for place in places if place["cityId"] == city_id]

    def get_all_places(self) -> list[PlaceRecord]:
        return list(_read_json(self.base_path / "city_places.json"))

    def get_media(self) -> list[MediaRecord]:
        return list(_read_json(self.base_path / "media_items.json"))

    def get_all_media_ratings(self) -> list[UserMediaRatingRecord]:
        output: list[UserMediaRatingRecord] = []
        for media in self.get_media():
            media_id = str(media.get("mediaId", "")).strip()
            if not media_id:
                continue
            for rating in media.get("userRatings", []):
                user_id = str(rating.get("userId", "")).strip()
                if not user_id:
                    continue
                output.append(
                    {
                        "userId": user_id,
                        "mediaId": media_id,
                        "rate": float(rating.get("rate", 0)),
                    }
                )
        return output

    def get_all_place_ratings(self) -> list[UserPlaceRatingRecord]:
        output: list[UserPlaceRatingRecord] = []
        for media in self.get_media():
            place_id = str(media.get("placeId", "")).strip()
            if not place_id:
                continue
            for rating in media.get("userRatings", []):
                user_id = str(rating.get("userId", "")).strip()
                if not user_id:
                    continue
                output.append(
                    {
                        "userId": user_id,
                        "placeId": place_id,
                        "rate": float(rating.get("rate", 0)),
                    }
                )
        return output


@lru_cache(maxsize=32)
def _read_json(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Mock JSON file must contain a list: {path}")
    return data
