from dataclasses import dataclass
from typing import Optional


@dataclass
class ChangeTrigger:
    """Represents a trigger for replanning a trip."""

    trigger_type: str
    description: str
    related_entity_id: Optional[int] = None
