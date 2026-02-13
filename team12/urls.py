from django.urls import path, include
from . import views

TEAM_PREFIX = "team12/"

urlpatterns = [
    path("", views.base, name="base"),
    path("ping/", views.ping, name="ping"),

    # 1. POST /team12/recommend/places/score
    path("places/score", views.ScoreCandidatePlacesView.as_view(), name="score-candidate-places"),

    # 2. GET /team12/recommend/regions
    path("regions", views.SuggestRegionsView.as_view(), name="suggest-regions"),

    # 3. GET /team12/recommend/regions/{region_id}/places
    path("regions/<str:region_id>/places", views.SuggestPlacesInRegionView.as_view(), name="suggest-places-in-region"),
]