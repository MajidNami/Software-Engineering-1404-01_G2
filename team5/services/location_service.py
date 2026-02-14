"""Helpers for extracting client IP and resolving nearest city."""

from __future__ import annotations

import json
import math
from ipaddress import ip_address
from urllib.error import URLError
from urllib.request import urlopen


def get_client_ip(request, *, ip_override: str | None = None) -> str | None:
    """Return client IP from query override, X-Forwarded-For or REMOTE_ADDR."""
    if ip_override:
        return ip_override.strip()

    forwarded_for = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if forwarded_for:
        # Standard format: "client_ip, proxy1, proxy2"
        first_ip = forwarded_for.split(",")[0].strip()
        if first_ip:
            return first_ip

    remote_addr = (request.META.get("REMOTE_ADDR") or "").strip()
    return remote_addr or None


def resolve_client_city(
    *,
    cities: list[dict],
    client_ip: str | None,
    preferred_city_id: str | None = None,
) -> dict | None:
    """
    Resolve nearest city from IP geolocation, then explicit city fallback.

    Returns a dict with:
    - city: matching city record from provider
    - source: how city was resolved
    - geo: raw geolocation payload (if available)
    """
    if client_ip:
        geo = _geolocate_ip(client_ip)
        if geo:
            if geo.get("city"):
                city = _match_city_name(cities, str(geo["city"]))
                if city:
                    return {"city": city, "source": "ip_city_name", "geo": geo}

            latitude = _to_float(geo.get("latitude"))
            longitude = _to_float(geo.get("longitude"))
            if latitude is not None and longitude is not None:
                city = _nearest_city_by_coordinates(cities, latitude=latitude, longitude=longitude)
                if city:
                    return {"city": city, "source": "ip_coordinates", "geo": geo}

    if preferred_city_id:
        city = _match_city_id(cities, preferred_city_id)
        if city:
            return {"city": city, "source": "manual_city_override", "geo": None}

    return None


def _geolocate_ip(client_ip: str) -> dict | None:
    """
    Resolve IP to city/coordinates using a public endpoint.

    Notes:
    - For private/local addresses, return None to avoid misleading results.
    - Keep timeout short to avoid slowing requests.
    """
    try:
        parsed_ip = ip_address(client_ip)
        if parsed_ip.is_private or parsed_ip.is_loopback or parsed_ip.is_unspecified:
            return None
    except ValueError:
        return None

    url = f"https://ipapi.co/{client_ip}/json/"
    try:
        with urlopen(url, timeout=1.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None

    if payload.get("error"):
        return None

    return {
        "city": payload.get("city"),
        "country": payload.get("country_name"),
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
    }


def _match_city_id(cities: list[dict], city_id: str) -> dict | None:
    normalized = city_id.strip().lower()
    for city in cities:
        if str(city.get("cityId", "")).strip().lower() == normalized:
            return city
    return None


def _match_city_name(cities: list[dict], city_name: str) -> dict | None:
    target = city_name.strip().lower()
    for city in cities:
        if str(city.get("cityName", "")).strip().lower() == target:
            return city
    return None


def _nearest_city_by_coordinates(cities: list[dict], *, latitude: float, longitude: float) -> dict | None:
    best_city: dict | None = None
    best_distance_km: float | None = None

    for city in cities:
        coords = city.get("coordinates") or []
        if len(coords) != 2:
            continue
        city_lat = _to_float(coords[0])
        city_lon = _to_float(coords[1])
        if city_lat is None or city_lon is None:
            continue
        distance = _haversine_km(latitude, longitude, city_lat, city_lon)
        if best_distance_km is None or distance < best_distance_km:
            best_distance_km = distance
            best_city = city

    return best_city


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_km * c


def _to_float(value) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None
