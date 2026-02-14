from dataclasses import dataclass


@dataclass
class Region:
    """A region returned from the facilities service."""
    id: str
    name: str
