from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router برای DRF ViewSets
router = DefaultRouter()
router.register(r'facilities', views.FacilityViewSet, basename='facility')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # Web Views
    path("", views.base, name='team4-base'),
    path("ping/", views.ping, name='team4-ping'),
    
    # API Routes
    path("api/", include(router.urls)),
    path("api/regions/search/", views.search_regions, name='search-regions'),
    path("api/navigation/route/", views.RoutingView.as_view(), name='route'),
]



