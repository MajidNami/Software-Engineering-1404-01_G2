from dataclasses import dataclass


@dataclass
class RecommendedItem:
    """A recommended item from the recommendation service."""

    id: int
    name: str
    item_type: str
    description: str
    rating: float
