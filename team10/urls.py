from django.urls import path, include
from . import views
from . import api_views

urlpatterns = [
    # HTML Views
    path("", views.base),
    path("ping/", views.ping),
    path("create-trip/", views.create_trip, name="create_trip"),

    # API endpoints
    path("api/trips/", api_views.create_trip_api, name="api_create_trip"),
    path("api/trips/<int:trip_id>/", api_views.get_trip_api, name="api_get_trip"),
    path("api/trips/<int:trip_id>/regenerate/", api_views.regenerate_trip_api, name="api_regenerate_trip"),
    path("api/trips/<int:trip_id>/budget-analysis/", api_views.analyze_budget_api, name="api_analyze_budget"),
]