from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..models.region import Region
from ..models.search_criteria import SearchCriteria
from ..models.facility_cost_estimate import FacilityCostEstimate
from ..models.travel_info import TravelInfo
from ...domain.models.facility import Facility


class FacilitiesServicePort(ABC):
    """Port for facilities service.
    
    This service provides:
    - Region search
    - Hotels and restaurants in regions
    - Facility details
    - Travel information (distance, time, cost) between facilities
    
    Note: Places of interest/attractions come from the Recommendation service,
    not from this service.
    """

    @abstractmethod
    def search_region(self, query: str) -> Optional[Region]:
        """Search for a region by name query.

        Args:
            query: The search string for finding a region.

        Returns:
            A Region with id and name, or None if not found.
        """
        pass

    @abstractmethod
    def find_facilities_in_area(self, criteria: SearchCriteria) -> List[Facility]:
        """Find facilities matching search criteria."""
        pass

    @abstractmethod
    def get_cost_estimate(
        self,
        facility_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> FacilityCostEstimate:
        """Get cost estimate for a facility during a period."""
        pass

    @abstractmethod
    def get_facility_by_id(self, facility_id: int) -> Optional[Facility]:
        """Get a facility by its ID.

        Args:
            facility_id: The unique identifier of the facility.

        Returns:
            The Facility object or None if not found.
        """
        pass

    @abstractmethod
    def get_facility_by_place_id(self, place_id: str, region_id: str) -> Optional[Facility]:
        """Get facility details for a place from the recommendation service.

        The recommendation service provides place_ids for attractions.
        This method returns the full facility details for that place.

        Args:
            place_id: The place identifier from recommendation service.
            region_id: The region ID where the place is located.

        Returns:
            The Facility object with full details, or None if not found.
        """
        pass

    @abstractmethod
    def get_hotels_in_region(self, region_id: str) -> List[Facility]:
        """Get all hotels in a region.

        Args:
            region_id: The region identifier.

        Returns:
            List of hotel facilities in the region.
        """
        pass

    @abstractmethod
    def get_restaurants_in_region(self, region_id: str) -> List[Facility]:
        """Get all restaurants in a region.

        Args:
            region_id: The region identifier.

        Returns:
            List of restaurant facilities in the region.
        """
        pass

    @abstractmethod
    def get_travel_info(self, from_facility_id: int, to_facility_id: int) -> TravelInfo:
        """Get travel information between two facilities.

        This includes distance, estimated travel time, recommended transport mode,
        and estimated travel cost.

        Args:
            from_facility_id: The starting facility ID.
            to_facility_id: The destination facility ID.

        Returns:
            TravelInfo with distance, time, transport mode, and cost.
        """
        pass
