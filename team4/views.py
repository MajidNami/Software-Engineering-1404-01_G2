from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ObjectDoesNotExist
from .fields import Point
import os
import requests
from dotenv import load_dotenv

from core.auth import api_login_required
from team4.models import Facility, Category, City, Amenity, Province, Village, RegionType, Favorite, Review
from team4.serializers import (
    FacilityListSerializer, FacilityDetailSerializer,
    FacilityNearbySerializer, FacilityComparisonSerializer,
    CategorySerializer, CitySerializer, AmenitySerializer,
    FacilityCreateSerializer, RegionSearchResultSerializer,
    FavoriteSerializer, ReviewSerializer, ReviewCreateSerializer,
    FacilityFilterSerializer, NearbyPlaceSerializer, RoutingRequestSerializer
)
from team4.services.facility_service import FacilityService
from team4.services.region_service import RegionService

TEAM_NAME = "team4"
load_dotenv()


# =====================================================
# Pagination
# =====================================================
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# =====================================================
# ViewSets
# =====================================================

class FacilityViewSet(viewsets.ModelViewSet):
    """
    List facilities with search and filters
    """
    queryset = Facility.objects.filter(status=True)
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FacilityListSerializer
        elif self.action == 'search':
            return FacilityListSerializer
        elif self.action == 'retrieve':
            return FacilityDetailSerializer
        elif self.action == 'create':
            return FacilityCreateSerializer
        return FacilityDetailSerializer
    
    def _get_region_filter_from_data(self, data):
        """
        Extract and validate region filter from request data with priority: village > city > province
        Returns tuple: (region_type, region_name)
        """
        village_name = data.get('village')
        city_name = data.get('city')
        province_name = data.get('province')
        
        if village_name:
            return ('village', village_name)
        elif city_name:
            return ('city', city_name)
        elif province_name:
            return ('province', province_name)
        return (None, None)
    
    def _validate_category(self, category_name):
        """Validate if category exists"""
        if not category_name:
            return True
        return Category.objects.filter(
            Q(name_en__iexact=category_name) | Q(name_fa__iexact=category_name)
        ).exists()
    
    def _validate_amenity(self, amenity_name):
        """Validate if amenity exists"""
        if not amenity_name:
            return True
        return Amenity.objects.filter(
            Q(name_en__iexact=amenity_name) | Q(name_fa__iexact=amenity_name)
        ).exists()
    
    def _apply_region_filter(self, queryset, region_type, region_name):
        """Apply region-based filtering"""
        if not region_name:
            return queryset
        
        if region_type == 'village':
            return queryset.filter(
                Q(village__name_fa__icontains=region_name) |
                Q(village__name_en__icontains=region_name)
            )
        elif region_type == 'city':
            return queryset.filter(
                Q(city__name_fa__icontains=region_name) |
                Q(city__name_en__icontains=region_name)
            )
        elif region_type == 'province':
            return queryset.filter(
                Q(city__province__name_fa__icontains=region_name) |
                Q(city__province__name_en__icontains=region_name)
            )
        return queryset
    
    def _apply_sorting(self, queryset, sort_by, region_name=None):
        """Apply sorting to queryset"""
        if sort_by == 'rating':
            return queryset.order_by('-avg_rating', '-review_count')
        elif sort_by == 'review_count':
            return queryset.order_by('-review_count')
        elif sort_by == 'distance' and region_name:
            sorted_facilities = FacilityService.sort_by_city_distance(queryset, region_name)
            return sorted_facilities if sorted_facilities else queryset.order_by('-avg_rating')
        return queryset.order_by('-avg_rating')
    
    def list(self, request):
        """
        List facilities with advanced filtering and sorting.
        
        Request Body:
        - name: Search in facility name (name_fa and name_en)
        - village: Filter by village name (highest priority)
        - city: Filter by city name (medium priority)
        - province: Filter by province name (lowest priority)
        - category: Filter by category name (must be valid)
        - amenity: Filter by amenity name (must be valid)
        - price_tier: Filter by price tier (free, budget, moderate, expensive, luxury)
        
        Query Parameters:
        - min_price, max_price: Price range filters
        - min_rating: Minimum rating filter
        - is_24_hour: 24-hour operation filter
        - sort: Sorting method (rating, review_count, distance)
        """
        # Validate request data
        serializer = FacilityFilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Extract and validate region filter
        region_type, region_name = self._get_region_filter_from_data(data)
        
        # Extract other parameters
        name_query = data.get('name')
        category_name = data.get('category')
        amenity_name = data.get('amenity')
        price_tier = data.get('price_tier')
        sort_by = request.query_params.get('sort', 'rating')
        
        # Validate category
        if category_name and not self._validate_category(category_name):
            return Response(
                {'error': f'Invalid category: {category_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate amenity
        if amenity_name and not self._validate_amenity(amenity_name):
            return Response(
                {'error': f'Invalid amenity: {amenity_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start with base queryset
        facilities = self.queryset
        
        # Apply name search filter
        if name_query:
            facilities = facilities.filter(
                Q(name_fa__icontains=name_query) |
                Q(name_en__icontains=name_query)
            )
        
        # Apply region filter
        facilities = self._apply_region_filter(facilities, region_type, region_name)
        
        # Apply category filter
        if category_name:
            facilities = facilities.filter(
                Q(category__name_en__iexact=category_name) |
                Q(category__name_fa__iexact=category_name)
            )
        
        # Apply amenity filter
        if amenity_name:
            facilities = facilities.filter(
                amenities__name_en__iexact=amenity_name
            ) | facilities.filter(
                amenities__name_fa__iexact=amenity_name)
        
        # Apply price tier filter
        if price_tier:
            facilities = facilities.filter(price_tier__iexact=price_tier)
        
        # Apply additional filters
        filters = {
            'min_price': request.query_params.get('min_price'),
            'max_price': request.query_params.get('max_price'),
            'min_rating': request.query_params.get('min_rating'),
            'is_24_hour': request.query_params.get('is_24_hour'),
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        if filters:
            facilities = FacilityService.filter_facilities(facilities, filters)
        
        # Apply sorting
        sorted_result = self._apply_sorting(facilities, sort_by, region_name)
        
        # Handle distance sorting special case
        if sort_by == 'distance' and isinstance(sorted_result, list):
            page = self.paginate_queryset([f['facility'] for f in sorted_result])
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(
                [f['facility'] for f in sorted_result],
                many=True
            )
            return Response(serializer.data)
        
        # Standard pagination
        page = self.paginate_queryset(sorted_result)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(sorted_result, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Search facilities with advanced filtering and sorting.
        
        Request Body:
        - name: Search in facility name (name_fa and name_en)
        - village: Filter by village name (highest priority)
        - city: Filter by city name (medium priority)
        - province: Filter by province name (lowest priority)
        - category: Filter by category name (must be valid)
        - amenity: Filter by amenity name (must be valid)
        - price_tier: Filter by price tier (free, budget, moderate, expensive, luxury)
        
        Query Parameters:
        - min_price, max_price: Price range filters
        - min_rating: Minimum rating filter
        - is_24_hour: 24-hour operation filter
        - sort: Sorting method (rating, review_count, distance)
        """
        # Validate request data
        serializer = FacilityFilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Extract and validate region filter
        region_type, region_name = self._get_region_filter_from_data(data)
        
        # Extract other parameters
        name_query = data.get('name')
        category_name = data.get('category')
        amenity_name = data.get('amenity')
        price_tier = data.get('price_tier')
        sort_by = request.query_params.get('sort', 'rating')
        
        # Validate category
        if category_name and not self._validate_category(category_name):
            return Response(
                {'error': f'Invalid category: {category_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate amenity
        if amenity_name and not self._validate_amenity(amenity_name):
            return Response(
                {'error': f'Invalid amenity: {amenity_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start with base queryset
        facilities = self.queryset
        
        # Apply name search filter
        if name_query:
            facilities = facilities.filter(
                Q(name_fa__icontains=name_query) |
                Q(name_en__icontains=name_query)
            )
        
        # Apply region filter
        facilities = self._apply_region_filter(facilities, region_type, region_name)
        
        # Apply category filter
        if category_name:
            facilities = facilities.filter(
                Q(category__name_en__iexact=category_name) |
                Q(category__name_fa__iexact=category_name)
            )
        
        # Apply amenity filter
        if amenity_name:
            facilities = facilities.filter(
                amenities__name_en__iexact=amenity_name
            ) | facilities.filter(
                amenities__name_fa__iexact=amenity_name
            )
        
        # Apply price tier filter
        if price_tier:
            facilities = facilities.filter(price_tier__iexact=price_tier)
        
        # Apply additional filters
        filters = {
            'min_price': request.query_params.get('min_price'),
            'max_price': request.query_params.get('max_price'),
            'min_rating': request.query_params.get('min_rating'),
            'is_24_hour': request.query_params.get('is_24_hour'),
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        if filters:
            facilities = FacilityService.filter_facilities(facilities, filters)
        
        # Apply sorting
        sorted_result = self._apply_sorting(facilities, sort_by, region_name)
        
        # Handle distance sorting special case
        if sort_by == 'distance' and isinstance(sorted_result, list):
            page = self.paginate_queryset([f['facility'] for f in sorted_result])
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(
                [f['facility'] for f in sorted_result],
                many=True
            )
            return Response(serializer.data)
        
        # Standard pagination
        page = self.paginate_queryset(sorted_result)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(sorted_result, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        try:
            facility = FacilityService.get_facility_details(pk)
            serializer = self.get_serializer(facility)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response(
                {'error': f'مکان با شناسه {pk} یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def nearby(self, request, pk=None):
        # Validate radius parameter
        radius_param = request.query_params.get('radius', 5)
        is_valid, radius, error_msg = FacilityService.validate_radius(radius_param)
        
        if not is_valid:
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        category_name = request.query_params.get('category')
        
        # Get nearby facilities with center facility
        center_facility, nearby_facilities = FacilityService.get_nearby_facilities(
            fac_id=pk,
            radius_km=radius,
            category_name=category_name
        )
        
        if center_facility is None:
            return Response(
                {'error': 'مکان مرجع یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not nearby_facilities:
            return Response(
                {'message': 'هیچ امکاناتی در این شعاع یافت نشد'},
                status=status.HTTP_200_OK
            )
        
        center_data = FacilityListSerializer(center_facility).data
        serializer = FacilityNearbySerializer(nearby_facilities, many=True)
        
        return Response({
            'center': center_data,
            'radius_km': radius,
            'count': len(nearby_facilities),
            'nearby_facilities': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def compare(self, request):
        """
        Compare multiple facilities side by side.
        Returns detailed comparison including prices, ratings, amenities, and distances.
        """
        facility_ids = request.data.get('facility_ids', [])
        
        if not facility_ids:
            return Response(
                {'error': 'لیست facility_ids الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comparison = FacilityService.compare_facilities(facility_ids)
        
        if 'error' in comparison:
            return Response(comparison, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(comparison)
    
    @action(detail=False, methods=['get'], url_path='nearby')
    def nearby_search(self, request):
        """
        Find nearby places from a specific location.
        
        Query Parameters:
        - lat: Latitude (required)
        - lng: Longitude (required)
        - radius: Search radius in meters (required)
        - categories: Comma-separated category names (optional)
        - price_tiers: Comma-separated price tiers (optional)
        
        Returns list of nearby facilities with distance in meters.
        """
        # Validate required parameters
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius')
        
        if not all([lat, lng, radius]):
            return Response(
                {'error': 'پارامترهای lat، lng و radius الزامی هستند'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lat = float(lat)
            lng = float(lng)
            radius_meters = int(radius)
            
            if not (-90 <= lat <= 90):
                raise ValueError('Latitude باید بین -90 تا 90 باشد')
            if not (-180 <= lng <= 180):
                raise ValueError('Longitude باید بین -180 تا 180 باشد')
            if radius_meters <= 0:
                raise ValueError('شعاع باید مثبت باشد')
                
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create center point
        center_point = Point(lng, lat)
        
        # Start with base queryset
        facilities = self.queryset
        
        # Filter by categories
        categories_param = request.query_params.get('categories')
        if categories_param:
            category_list = [c.strip() for c in categories_param.split(',')]
            facilities = facilities.filter(
                Q(category__name_en__in=category_list) |
                Q(category__name_fa__in=category_list)
            )
        
        # Filter by price tiers
        price_tiers_param = request.query_params.get('price_tiers')
        if price_tiers_param:
            tier_list = [t.strip() for t in price_tiers_param.split(',')]
            facilities = facilities.filter(price_tier__in=tier_list)
        
        # Calculate distances and filter by radius
        nearby_places = []
        radius_km = radius_meters / 1000.0
        
        for facility in facilities:
            if facility.location:
                try:
                    distance_km = facility.calculate_distance_to(center_point)
                    if distance_km and distance_km <= radius_km:
                        nearby_places.append({
                            'facility': facility,
                            'distance_meters': distance_km * 1000  # Convert to meters
                        })
                except:
                    continue
        
        # Sort by distance
        nearby_places.sort(key=lambda x: x['distance_meters'])
        
        # Paginate
        page = self.paginate_queryset(nearby_places)
        if page is not None:
            serializer = NearbyPlaceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = NearbyPlaceSerializer(nearby_places, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """
        Retrieve reviews for a specific facility.
        Returns paginated list of approved reviews with user information.
        """
        try:
            facility = Facility.objects.get(fac_id=pk)
        except Facility.DoesNotExist:
            return Response(
                {'error': 'مکان یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get approved reviews
        reviews = Review.objects.filter(
            facility=facility,
            is_approved=True
        ).select_related('user').order_by('-created_at')
        
        # Filter by rating
        rating = request.query_params.get('rating')
        if rating:
            try:
                rating_int = int(rating)
                reviews = reviews.filter(rating=rating_int)
            except ValueError:
                pass
        
        # Pagination
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(
            reviews,
            many=True,
            context={'request': request}
        )
        return Response({
            'count': reviews.count(),
            'reviews': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def emergency(self, request):
        """
        Get list of emergency facilities (hospitals, clinics, pharmacies).
        
        Query Parameters:
        - city: City name (optional)
        - lat: Latitude coordinate (optional)
        - lng: Longitude coordinate (optional)
        - radius: Search radius in kilometers (default: 10)
        
        When lat/lng provided, returns facilities sorted by distance.
        """
        # Filter emergency facilities
        facilities = self.queryset.filter(category__is_emergency=True)
        
        # Filter by city
        city_name = request.query_params.get('city')
        if city_name:
            facilities = facilities.filter(
                Q(city__name_fa__icontains=city_name) |
                Q(city__name_en__icontains=city_name)
            )
        
        # Filter by geographic location
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius', 10)
        
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
                radius = float(radius)
                
                from .fields import Point
                user_location = Point(lng, lat, srid=4326)
                
                # Calculate distance and filter
                facilities_with_distance = []
                for facility in facilities:
                    distance = facility.calculate_distance_to(user_location)
                    if distance and distance <= radius:
                        facilities_with_distance.append({
                            'facility': facility,
                            'distance_km': round(distance, 2)
                        })
                
                # Sort by distance
                facilities_with_distance.sort(key=lambda x: x['distance_km'])
                
                # Pagination
                page = self.paginate_queryset([f['facility'] for f in facilities_with_distance])
                if page is not None:
                    # Add distance to serializer data
                    serializer = self.get_serializer(page, many=True)
                    data = serializer.data
                    for i, item in enumerate(data):
                        item['distance_km'] = facilities_with_distance[i]['distance_km']
                    return self.get_paginated_response(data)
                
                serializer = self.get_serializer(
                    [f['facility'] for f in facilities_with_distance],
                    many=True
                )
                data = serializer.data
                for i, item in enumerate(data):
                    item['distance_km'] = facilities_with_distance[i]['distance_km']
                return Response({
                    'count': len(data),
                    'results': data
                })
            
            except (ValueError, TypeError):
                return Response(
                    {'error': 'مختصات جغرافیایی نامعتبر است'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Without location filter
        facilities = facilities.order_by('-avg_rating')
        
        # Pagination
        page = self.paginate_queryset(facilities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(facilities, many=True)
        return Response({
            'count': facilities.count(),
            'results': serializer.data
        })


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing facility categories.
    
    Endpoints:
    - GET /api/categories/     → List all facility categories
    - GET /api/categories/{id}/ → Retrieve category details
    
    Categories include hotels, restaurants, hospitals, museums, etc.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")


# =====================================================
# Region Search API
# =====================================================

@api_view(['GET'])
def search_regions(request):
    """
    Search for regions (provinces, cities, villages) by name.
    
    Query Parameters:
    - query: Search query string (required)
    - region_type: Filter by type - 'province', 'city', or 'village' (optional)
    
    Returns matching regions with their type and geographic information.
    """
    query = request.query_params.get('query', '').strip()
    region_type = request.query_params.get('region_type', '').strip().lower()
    
    # Validate query parameter
    if not query:
        return Response(
            {'error': 'پارامتر query الزامی است'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate region_type
    is_valid, error_msg = RegionService.validate_region_type(region_type)
    if not is_valid:
        return Response(
            {'error': error_msg},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Search via Service
    results = RegionService.search_regions(query, region_type or None)
    
    # Serialize results
    serializer = RegionSearchResultSerializer(results, many=True)
    
    return Response({
        'count': len(results),
        'regions': serializer.data
    })


# =====================================================
# Favorite ViewSet
# =====================================================

class FavoriteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user favorites.
    
    Endpoints:
    - GET /api/favorites/              → List user's favorite facilities
    - POST /api/favorites/             → Add facility to favorites
    - DELETE /api/favorites/{id}/      → Remove facility from favorites
    - POST /api/favorites/toggle/      → Toggle favorite status
    - GET /api/favorites/check/        → Check if facility is favorited
    """
    serializer_class = FavoriteSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'favorite_id'
    
    def get_queryset(self):
        # Only current user's favorites
        return Favorite.objects.filter(user=self.request.user).select_related(
            'facility',
            'facility__category',
            'facility__city',
            'facility__city__province'
        )
    
    def create(self, request):
        """Add a facility to user's favorites."""
        facility_id = request.query_params.get('facility')
        data = request.data.copy() if request.data else {}
        if facility_id:
            data['facility'] = facility_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_id=self.request.user.pk)
        
        return Response(
            {
                'message': 'مکان با موفقیت به علاقه‌مندی‌ها اضافه شد',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    def destroy(self, request, *args, **kwargs):
        # We grab the ID from the URL using the name you defined in lookup_field
        favorite_id = kwargs.get('favorite_id')
        
        try:
            # Filter by both ID and User to ensure people can't delete 
            # other people's favorites by guessing the ID
            instance = Favorite.objects.get(
                favorite_id=favorite_id, 
                user_id=request.user.pk
            )
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Favorite.DoesNotExist:
            return Response(
                {"detail": "علاقه‌مندی پیدا نشد."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        facility_id = request.data.get('facility') or request.query_params.get('facility')
        if not facility_id:
            return Response({"detail": "Facility ID required"}, status=400)

        # For development: handle anonymous users
        if not request.user or not request.user.is_authenticated:
            return Response({
                "detail": "Authentication required. Please login first.",
                "status": "error"
            }, status=401)

        # Get the facility object (lives in the same DB as Favorite)
        facility = get_object_or_404(Facility, pk=facility_id)

        # 1. Look for existing favorite using IDs only
        favorite_filter = Favorite.objects.filter(
            user_id=request.user.pk, 
            facility_id=facility.pk
        )

        if favorite_filter.exists():
            # 2. If it exists, remove it
            favorite_filter.delete()
            return Response({"status": "removed", "favorited": False})
        else:
            # 3. If it doesn't, create it using user_id=... (The Multi-DB Fix)
            Favorite.objects.create(
                user_id=str(request.user.pk), # Use the ID value, not the object
                facility=facility             # This is okay because it's in the same DB
            )
            return Response({"status": "added", "favorited": True})

    @action(detail=False, methods=['get'])
    def check(self, request):
        facility_id = request.query_params.get('facility')
        
        if not facility_id:
            return Response(
                {'error': 'شناسه مکان الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # FIX: Use user_id=request.user.pk to bypass the Router error
        # We use .filter().exists() because it is much faster than .get()
        is_favorite = Favorite.objects.filter(
            user_id=request.user.pk,
            facility_id=facility_id
        ).exists()
        
        return Response({
            'is_favorite': is_favorite,
            'facility_id': facility_id
        })


# =====================================================
# Review ViewSet
# =====================================================

class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing facility reviews and ratings.
    
    Endpoints:
    - GET /api/reviews/                    → List all reviews (with filters)
    - GET /api/reviews/{id}/               → Retrieve review details
    - POST /api/reviews/                   → Create a new review
    - PUT/PATCH /api/reviews/{id}/         → Update existing review
    - DELETE /api/reviews/{id}/            → Delete a review
    
    Note: Users can only edit/delete their own reviews unless they are staff.
    """
    pagination_class = StandardResultsSetPagination
    lookup_field = 'review_id'
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def get_queryset(self):
        queryset = Review.objects.select_related(
            'user',
            'facility',
            'facility__category',
            'facility__city'
        )
        
        # Filter by facility
        facility_id = self.request.query_params.get('facility')
        if facility_id:
            queryset = queryset.filter(facility_id=facility_id)
        
        # Filter by user
        user_only = self.request.query_params.get('user_only')
        if user_only and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by rating
        rating = self.request.query_params.get('rating')
        if rating:
            try:
                rating_int = int(rating)
                queryset = queryset.filter(rating=rating_int)
            except ValueError:
                pass
        
        # Only approved reviews for non-staff users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        return queryset.order_by('-created_at')
    
    def create(self, request):
        """Submit a new review for a facility."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {
                'message': 'نظر شما با موفقیت ثبت شد',
                'data': ReviewSerializer(
                    serializer.instance,
                    context={'request': request}
                ).data
            },
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, pk=None, partial=False):
        """Update an existing review. Users can only update their own reviews."""
        try:
            review = self.get_queryset().get(review_id=pk)
            
            # Check ownership
            if review.user != request.user and not request.user.is_staff:
                return Response(
                    {'error': 'شما مجاز به ویرایش این نظر نیستید'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = self.get_serializer(
                review,
                data=request.data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({
                'message': 'نظر با موفقیت ویرایش شد',
                'data': serializer.data
            })
        
        except Review.DoesNotExist:
            return Response(
                {'error': 'نظر یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def destroy(self, request, pk=None):
        """Delete a review. Users can only delete their own reviews."""
        try:
            review = self.get_queryset().get(review_id=pk)
            
            # Check ownership
            if review.user != request.user and not request.user.is_staff:
                return Response(
                    {'error': 'شما مجاز به حذف این نظر نیستید'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            review.delete()
            return Response(
                {'message': 'نظر با موفقیت حذف شد'},
                status=status.HTTP_200_OK
            )
        
        except Review.DoesNotExist:
            return Response(
                {'error': 'نظر یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
       
class RoutingView(APIView):
    """
    API View to handle routing requests via an external Map Service.
    """

    def post(self, request):
        # Your logic remains exactly the same
        serializer = RoutingRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        origin_point = serializer.validated_data['origin']
        dest_point = serializer.validated_data['destination']
        
        origin_str = f"{origin_point.latitude},{origin_point.longitude}"
        dest_str = f"{dest_point.latitude},{dest_point.longitude}"
        
        service_url = "https://api.neshan.org/v4/direction"
        api_key = os.getenv('MAP_SERVICE_KEY')
        
        params = {
            'type': serializer.validated_data['type'],
            'origin': origin_str,
            'destination': dest_str,
            'avoidTrafficZone': str(serializer.validated_data.get('avoidTrafficZone', False)).lower(),
            'avoidOddEvenZone': str(serializer.validated_data.get('avoidOddEvenZone', False)).lower(),
            'alternative': str(serializer.validated_data.get('alternative', False)).lower(),
        }

        try:
            response = requests.get(service_url, headers={'Api-Key': api_key}, params=params, timeout=10)
            result = response.json()

            if response.status_code == 200:
                result['internal_air_distance_km'] = round(origin_point.distance(dest_point), 3)
                return Response(result, status=status.HTTP_200_OK)
            
            return Response(
                {
                    "detail": "خطا در دریافت اطلاعات از سرویس نقشه. لطفا ورودی‌ها را بررسی کنید.",
                    "service_response": result
                }, 
                status=response.status_code
            )
            
        except requests.exceptions.RequestException:
            return Response(
                {"detail": "خطا در برقراری ارتباط با سرویس نقشه. لطفاً وضعیت اینترنت را بررسی کنید."}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )