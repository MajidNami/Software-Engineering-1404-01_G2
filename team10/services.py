"""
Service instances for Team10 application.

This module provides singleton instances of application services that can be
imported and reused across the application.
"""

from .infrastructure.clients.facilities_client import MockFacilitiesClient
from .infrastructure.clients.recommendation_client import MockRecommendationClient
from .infrastructure.clients.wiki_client import MockWikiClient
from .application.services.trip_planning_service_impl import TripPlanningServiceImpl

# Singleton infrastructure service instances
facilities_service = MockFacilitiesClient()
recommendation_service = MockRecommendationClient()
wiki_service = MockWikiClient()

# Singleton application service with injected dependencies
trip_planning_service = TripPlanningServiceImpl(
    facilities_service=facilities_service,
    recommendation_service=recommendation_service,
    wiki_service=wiki_service,
)

__all__ = [
    'facilities_service',
    'recommendation_service',
    'wiki_service',
    'trip_planning_service',
]
