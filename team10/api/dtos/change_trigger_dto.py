from dataclasses import dataclass
from typing import Optional


@dataclass
class ChangeTriggerDto:
    """DTO for change trigger."""

    trigger_type: str
    description: str
    related_entity_id: Optional[int] = None
