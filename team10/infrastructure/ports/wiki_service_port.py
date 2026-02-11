from abc import ABC, abstractmethod

from ..models.destination_info import DestinationInfo


class WikiServicePort(ABC):
    """Port for wiki/knowledge service."""

    @abstractmethod
    def is_valid_destination(self, destination_name: str) -> bool:
        """Check if a destination is valid and has information."""
        pass

    @abstractmethod
    def get_destination_basic_info(self, destination_name: str) -> DestinationInfo:
        """Get basic information about a destination."""
        pass
