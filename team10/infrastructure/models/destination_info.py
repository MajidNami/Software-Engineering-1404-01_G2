from dataclasses import dataclass


@dataclass
class DestinationInfo:
    """Information about a destination from Wiki service."""

    name: str
    description: str
    country: str
    region: str
