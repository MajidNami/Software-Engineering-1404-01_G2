from django.urls import path
from . import views

urlpatterns = [
    path("", views.front),
    path("ping/", views.ping),
]