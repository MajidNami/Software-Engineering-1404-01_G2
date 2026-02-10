"""
Main URL configuration for Team 8 Backend
"""
from django.urls import path, include

urlpatterns = [
    path('', include('tourism.urls')),
]
