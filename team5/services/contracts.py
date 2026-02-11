"""Data contracts and API defaults for Team5 recommendation endpoints."""

from typing import TypedDict


DEFAULT_LIMIT = 20
POPULAR_MIN_OVERALL_RATE = 4.0
POPULAR_MIN_VOTES = 5
PERSONALIZED_MIN_USER_RATE = 4.0


class CityRecord(TypedDict):
    cityId: str
    cityName: str
    coordinates: list[float]


class PlaceRecord(TypedDict):
    placeId: str
    cityId: str
    placeName: str
    coordinates: list[float]


class UserRatingRecord(TypedDict):
    userId: str
    rate: float


class MediaRecord(TypedDict):
    mediaId: str
    placeId: str
    title: str
    caption: str
    overallRate: float
    ratingsCount: int
    userRatings: list[UserRatingRecord]
