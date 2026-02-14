"""Mock data provider backed by JSON files."""

import json
from functools import lru_cache
from pathlib import Path

from .contracts import CityRecord, MediaRecord, PlaceRecord
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


@lru_cache(maxsize=32)
def _read_json(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Mock JSON file must contain a list: {path}")
    return data
