from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import test, ok, TripViewSet, TripDayViewSet, TripItemViewSet

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
]
