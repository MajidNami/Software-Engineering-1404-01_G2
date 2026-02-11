from abc import ABC, abstractmethod
from typing import List
from datetime import datetime

from ...domain.models.facility import Facility
from ..models.search_criteria import SearchCriteria
from ..models.facility_cost_estimate import FacilityCostEstimate


class FacilitiesServicePort(ABC):
    """Port for facilities service."""

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
