from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import test, ok, TripViewSet, TripDayViewSet, TripItemViewSet, suggest_destinations, get_trip_cost_breakdown

router = DefaultRouter()
router.register(r'trips', TripViewSet, basename='trip')
router.register(r'trip-days', TripDayViewSet, basename='trip-day')
router.register(r'items', TripItemViewSet, basename='item')

urlpatterns = [
    path("test/", test),
    path("trip-plan/trips", ok),
    path(
        'days/<int:pk>/items/bulk/',
        TripDayViewSet.as_view({'post': 'create_items_bulk'}),
        name='day-items-bulk'
    ),
    path('', include(router.urls)),
    path('trips/generate/',
         TripViewSet.as_view({'post': 'generate_trip'}),
         name='trip-generate'),

    # API 2: Destination Suggestion
    path('destinations/suggest/',
         suggest_destinations,
         name='destinations-suggest'),

    # API 3: Alternatives Recommendation
    path('items/<int:pk>/alternatives/',
         TripItemViewSet.as_view({'get': 'get_alternatives'}),
         name='item-alternatives'),

    # API 4: Cost Calculation
    path('trips/<int:trip_id>/cost/',
         get_trip_cost_breakdown,
         name='trip-cost'),

    # API 5: Guest to User Conversion
    path('trips/<int:pk>/claim/',
         TripViewSet.as_view({'post': 'claim'}),
         name='trip-claim'),
]
