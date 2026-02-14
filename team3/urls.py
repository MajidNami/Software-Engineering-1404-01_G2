from django.urls import path
from . import views

urlpatterns = [
    path("", views.base),
    path("ping/", views.ping),
    path("health/", views.health),
    path("api/interests/", views.upsert_interests),
    path("api/recommendations/personalized/", views.personalized_recommendations),
    path("api/recommendations/contextual/", views.contextual_recommendations),
    path("api/recommendations/location/", views.recommendations_by_location),
    path("api/recommendations/score-candidates/", views.score_candidates),
    path("api/recommendations/suggest-destinations/", views.suggest_destinations),
    path("api/recommendations/suggest-by-region/", views.suggest_by_region),
    path("api/recommendations/<str:user_id>/", views.list_user_recommendations),
    path("api/recommendations/reason/<str:recommendation_id>/", views.recommendation_reason),
    path("api/interactions/", views.record_interaction),
    path("api/feedback/", views.submit_feedback),
]
