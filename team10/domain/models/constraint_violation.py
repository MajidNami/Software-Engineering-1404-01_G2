from dataclasses import dataclass


@dataclass
class ConstraintViolation:
    """Represents a violation of a trip constraint."""

    description: str
    constraint_type: str
    severity: int
