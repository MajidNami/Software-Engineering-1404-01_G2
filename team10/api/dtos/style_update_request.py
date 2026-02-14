from dataclasses import dataclass
from typing import List


@dataclass
class StyleUpdateRequest:
    """Request DTO for regenerating trip by styles."""

    styles: List[str]
