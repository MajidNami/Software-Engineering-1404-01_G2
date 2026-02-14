from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name="base"),
    path("ping/", views.ping, name="ping"),

    # POST /team12/recommend/places/score
    path("recommend/places/score/", views.ScoreCandidatePlacesView.as_view(), name="score-places"),

    # GET /team12/recommend/regions
    path("recommend/regions/", views.SuggestRegionsView.as_view(), name="suggest-regions"),

    # GET /team12/recommend/regions/{region_id}/places
    path("recommend/regions/<str:region_id>/places/", views.SuggestPlacesInRegionView.as_view(),
         name="suggest-places-in-region"),
]