from django.urls import path, include
from . import views
from . import api_views

app_name = "team10"

urlpatterns = [
    # test
    path("ping/", views.ping),

    # HTML Views
    path("", views.home, name="home"),
    path("trips/", views.trips_list, name="trips_list"),


    path("create-trip/", views.create_trip, name="create_trip"),
  
    path("trips/<int:trip_id>/", views.trip_detail, name="trip_detail"),
    path("trips/<int:trip_id>/cost/", views.trip_cost, name="trip_cost"),
    path("trips/<int:trip_id>/styles/", views.trip_styles, name="trip_styles"),
    path("trips/<int:trip_id>/replan/", views.trip_replan, name="trip_replan"),

    # API endpoints
    path("api/trips/", api_views.create_trip_api, name="api_create_trip"),
    path("api/trips/<int:trip_id>/", api_views.get_trip_api, name="api_get_trip"),
    path("api/trips/<int:trip_id>/regenerate/", api_views.regenerate_trip_api, name="api_regenerate_trip"),
    path("api/trips/<int:trip_id>/budget-analysis/", api_views.analyze_budget_api, name="api_analyze_budget"),
]