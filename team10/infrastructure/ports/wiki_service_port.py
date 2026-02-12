from abc import ABC, abstractmethod


class WikiServicePort(ABC):
    """Port for wiki/knowledge service.
    
    This service provides basic information about destinations.
    If a destination is not valid or not found, it returns an
    empty string (the caller handles displaying nothing to the user).
    """

    @abstractmethod
    def get_destination_basic_info(self, destination_name: str) -> str:
        """Get basic description about a destination.
        
        Args:
            destination_name: The name of the destination to look up.
            
        Returns:
            A description string for the destination.
            If the destination is not found, returns an empty string.
        """
        pass
