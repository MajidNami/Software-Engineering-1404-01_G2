"""
URL configuration for Team 8 Backend API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .viewsets import (
    CategoryViewSet, PlaceViewSet, MediaViewSet,
    RatingViewSet, CommentViewSet, ReportViewSet,
    NotificationViewSet
)

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'places', PlaceViewSet, basename='place')
router.register(r'media', MediaViewSet, basename='media')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # Base views (for compatibility with Core)
    path("", views.base, name='team8-base'),
    path("ping/", views.ping, name='team8-ping'),
    
    # API endpoints
    path("api/", include(router.urls)),
    
    # Health check
    path("health/", views.health, name='team8-health'),
]