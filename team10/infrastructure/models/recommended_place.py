from dataclasses import dataclass


@dataclass
class RecommendedPlace:
    """A recommended place from the recommender service."""
    place_id: str
    score: float
