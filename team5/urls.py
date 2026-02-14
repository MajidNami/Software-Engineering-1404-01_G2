from django.urls import path
from . import views

urlpatterns = [
    path("", views.base),
    path("ping/", views.ping),
    path("api/cities/", views.get_cities),
    path("api/places/city/<str:city_id>/", views.get_city_places),
    path("api/media/", views.get_media),
    path("api/users/", views.get_registered_users),
    path("api/users/<str:user_id>/ratings/", views.get_user_ratings),
    path("api/recommendations/popular/", views.get_popular_recommendations),
    path("api/recommendations/nearest/", views.get_nearest_recommendations),
    path("api/recommendations/personalized/", views.get_personalized_recommendations),
    path("api/users/<str:user_id>/interests/", views.get_user_interests),
]