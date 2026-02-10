from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views, auth_views
from .viewsets import (
    ProvinceViewSet, CityViewSet, CategoryViewSet,
    PlaceViewSet, MediaViewSet, PostViewSet,
    RatingViewSet, NotificationViewSet, ReportViewSet,
)

router = DefaultRouter()
router.register(r'provinces', ProvinceViewSet, basename='province')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'places', PlaceViewSet, basename='place')
router.register(r'media', MediaViewSet, basename='media')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'ratings', RatingViewSet, basename='rating')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    # Utility
    path('ping/', views.ping, name='team8-ping'),
    path('health/', views.health, name='team8-health'),

    # Auth (standalone)
    path('api/auth/register/', auth_views.register, name='auth-register'),
    path('api/auth/login/', auth_views.login, name='auth-login'),
    path('api/auth/logout/', auth_views.logout, name='auth-logout'),
    path('api/auth/verify/', auth_views.verify_token, name='auth-verify'),
    path('api/auth/profile/', auth_views.get_profile, name='auth-profile'),

    # API
    path('api/', include(router.urls)),
]
