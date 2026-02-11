"""Provider abstraction for Team5 data sources."""

from abc import ABC, abstractmethod

from .contracts import CityRecord, MediaRecord, PlaceRecord


class DataProvider(ABC):
    """Abstract source of recommendation input data."""

    @abstractmethod
    def get_cities(self) -> list[CityRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_city_places(self, city_id: str) -> list[PlaceRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_all_places(self) -> list[PlaceRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_media(self) -> list[MediaRecord]:
        raise NotImplementedError
