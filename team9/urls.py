from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name='home'),
    path("ping/", views.ping, name='ping'),
    path("map/", views.map_view, name='map_view'),
]
