from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ObjectDoesNotExist
from .fields import Point

from core.auth import api_login_required
from team4.models import Facility, Category, City, Amenity, Province, Village, RegionType, Favorite, Review
from team4.serializers import (
    FacilityListSerializer, FacilityDetailSerializer,
    FacilityNearbySerializer, FacilityComparisonSerializer,
    CategorySerializer, CitySerializer, AmenitySerializer,
    FacilityCreateSerializer, RegionSearchResultSerializer,
    FavoriteSerializer, ReviewSerializer, ReviewCreateSerializer
)
from team4.services.facility_service import FacilityService
from team4.services.region_service import RegionService

TEAM_NAME = "team4"


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
    ViewSet برای مدیریت امکانات
    
    APIs:
    - GET /api/facilities/              → لیست امکانات با جستجو و فیلتر
    - GET /api/facilities/{id}/         → جزئیات یک مکان
    - GET /api/facilities/{id}/nearby/  → امکانات نزدیک
    - POST /api/facilities/compare/     → مقایسه هتل‌ها
    """
    queryset = Facility.objects.filter(status=True)
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FacilityListSerializer
        elif self.action == 'retrieve':
            return FacilityDetailSerializer
        elif self.action == 'create':
            return FacilityCreateSerializer
        return FacilityDetailSerializer
    
    def list(self, request):
        # دریافت پارامترها
        city_name = request.query_params.get('city')
        category_name = request.query_params.get('category')
        sort_by = request.query_params.get('sort', 'rating')
        
        # جستجو
        facilities = FacilityService.search_facilities(
            city_name=city_name,
            category_name=category_name
        )
        
        # فیلتر
        filters = {
            'min_price': request.query_params.get('min_price'),
            'max_price': request.query_params.get('max_price'),
            'min_rating': request.query_params.get('min_rating'),
            'amenities': request.query_params.get('amenities'),
            'is_24_hour': request.query_params.get('is_24_hour'),
        }
        
        # حذف فیلترهای None
        filters = {k: v for k, v in filters.items() if v is not None}
        
        if filters:
            facilities = FacilityService.filter_facilities(facilities, filters)
        
        # مرتب‌سازی
        if sort_by == 'rating':
            facilities = facilities.order_by('-avg_rating', '-review_count')
        elif sort_by == 'review_count':
            facilities = facilities.order_by('-review_count')
        elif sort_by == 'distance' and city_name:
            # استفاده از Service برای مرتب‌سازی بر اساس فاصله
            sorted_facilities = FacilityService.sort_by_city_distance(facilities, city_name)
            
            if sorted_facilities:
                # استفاده از pagination
                page = self.paginate_queryset([f['facility'] for f in sorted_facilities])
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)
                
                serializer = self.get_serializer(
                    [f['facility'] for f in sorted_facilities],
                    many=True
                )
                return Response(serializer.data)
            # اگر شهر یافت نشد، fallback به sorting معمولی
            facilities = facilities.order_by('-avg_rating')
        
        # Pagination
        page = self.paginate_queryset(facilities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(facilities, many=True)
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
        # Validation شعاع
        radius_param = request.query_params.get('radius', 5)
        is_valid, radius, error_msg = FacilityService.validate_radius(radius_param)
        
        if not is_valid:
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        category_name = request.query_params.get('category')
        
        # دریافت امکانات نزدیک با center_facility
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
        FR-8: مقایسه هتل‌ها
        
        Body:
            {
                "facility_ids": [123, 125, 130]
            }
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
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """
        دریافت نظرات یک مکان
        
        Query Parameters:
        - rating: فیلتر بر اساس امتیاز (1-5)
        """
        try:
            facility = Facility.objects.get(fac_id=pk)
        except Facility.DoesNotExist:
            return Response(
                {'error': 'مکان یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # دریافت نظرات تایید شده
        reviews = Review.objects.filter(
            facility=facility,
            is_approved=True
        ).select_related('user').order_by('-created_at')
        
        # فیلتر بر اساس امتیاز
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
        دریافت لیست امکانات اضطراری
        
        Query Parameters:
        - city: نام شهر (اختیاری)
        - lat: عرض جغرافیایی (اختیاری)
        - lng: طول جغرافیایی (اختیاری)
        - radius: شعاع جستجو به کیلومتر (پیش‌فرض: 10)
        """
        # فیلتر امکانات اضطراری
        facilities = self.queryset.filter(category__is_emergency=True)
        
        # فیلتر بر اساس شهر
        city_name = request.query_params.get('city')
        if city_name:
            facilities = facilities.filter(
                Q(city__name_fa__icontains=city_name) |
                Q(city__name_en__icontains=city_name)
            )
        
        # فیلتر بر اساس موقعیت جغرافیایی
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
                
                # محاسبه فاصله و فیلتر
                facilities_with_distance = []
                for facility in facilities:
                    distance = facility.calculate_distance_to(user_location)
                    if distance and distance <= radius:
                        facilities_with_distance.append({
                            'facility': facility,
                            'distance_km': round(distance, 2)
                        })
                
                # مرتب‌سازی بر اساس فاصله
                facilities_with_distance.sort(key=lambda x: x['distance_km'])
                
                # Pagination
                page = self.paginate_queryset([f['facility'] for f in facilities_with_distance])
                if page is not None:
                    # اضافه کردن فاصله به serializer data
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
        
        # بدون فیلتر موقعیت
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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.select_related('province').all()
    serializer_class = CitySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        province = self.request.query_params.get('province')
        
        if province:
            queryset = queryset.filter(province__name_fa__icontains=province)
        
        return queryset


class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer


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
    جستجوی مناطق (استان، شهر، روستا)
    
    Query Parameters:
    - query: متن جستجو (الزامی)
    - region_type: نوع منطقه - province, city, village (اختیاری)
    
    Response:
    {
        "regions": [
            {
                "id": "string",
                "name": "string",
                "parent_region_id": "string",
                "parent_region_name": "string"
            }
        ]
    }
    """
    query = request.query_params.get('query', '').strip()
    region_type = request.query_params.get('region_type', '').strip().lower()
    
    # Validation
    if not query:
        return Response(
            {'error': 'پارامتر query الزامی است'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # اعتبارسنجی region_type
    is_valid, error_msg = RegionService.validate_region_type(region_type)
    if not is_valid:
        return Response(
            {'error': error_msg},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # جستجو از طریق Service
    results = RegionService.search_regions(query, region_type or None)
    
    # سریالایز نتایج
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
    ViewSet برای مدیریت علاقه‌مندی‌ها
    
    APIs:
    - GET /api/favorites/              → لیست علاقه‌مندی‌های کاربر
    - POST /api/favorites/             → افزودن به علاقه‌مندی‌ها
    - DELETE /api/favorites/{id}/      → حذف از علاقه‌مندی‌ها
    """
    serializer_class = FavoriteSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        # فقط علاقه‌مندی‌های کاربر جاری
        return Favorite.objects.filter(user=self.request.user).select_related(
            'facility',
            'facility__category',
            'facility__city',
            'facility__city__province'
        )
    
    def create(self, request):
        """افزودن مکان به علاقه‌مندی‌ها"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {
                'message': 'مکان با موفقیت به علاقه‌مندی‌ها اضافه شد',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    def destroy(self, request, pk=None):
        """حذف مکان از علاقه‌مندی‌ها"""
        try:
            favorite = self.get_queryset().get(favorite_id=pk)
            favorite.delete()
            return Response(
                {'message': 'مکان از علاقه‌مندی‌ها حذف شد'},
                status=status.HTTP_200_OK
            )
        except Favorite.DoesNotExist:
            return Response(
                {'error': 'علاقه‌مندی یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        افزودن/حذف مکان از علاقه‌مندی‌ها
        
        Body:
            {
                "facility": 123
            }
        
        Response:
            {
                "message": "added" یا "removed",
                "is_favorite": true/false
            }
        """
        facility_id = request.data.get('facility')
        
        if not facility_id:
            return Response(
                {'error': 'شناسه مکان الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            facility = Facility.objects.get(fac_id=facility_id)
        except Facility.DoesNotExist:
            return Response(
                {'error': 'مکان یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        favorite = Favorite.objects.filter(
            user=request.user,
            facility=facility
        ).first()
        
        if favorite:
            # حذف از علاقه‌مندی‌ها
            favorite.delete()
            return Response({
                'message': 'removed',
                'is_favorite': False
            })
        else:
            # افزودن به علاقه‌مندی‌ها
            Favorite.objects.create(
                user=request.user,
                facility=facility
            )
            return Response({
                'message': 'added',
                'is_favorite': True
            }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """
        بررسی وضعیت علاقه‌مندی یک مکان
        
        Query Parameters:
        - facility: شناسه مکان
        
        Response:
            {
                "is_favorite": true/false
            }
        """
        facility_id = request.query_params.get('facility')
        
        if not facility_id:
            return Response(
                {'error': 'شناسه مکان الزامی است'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_favorite = Favorite.objects.filter(
            user=request.user,
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
    ViewSet برای مدیریت نظرات
    
    APIs:
    - GET /api/reviews/                    → لیست همه نظرات (با فیلتر)
    - GET /api/reviews/{id}/               → جزئیات یک نظر
    - POST /api/reviews/                   → ثبت نظر جدید
    - PUT/PATCH /api/reviews/{id}/         → ویرایش نظر
    - DELETE /api/reviews/{id}/            → حذف نظر
    - GET /api/facilities/{id}/reviews/    → نظرات یک مکان (در FacilityViewSet)
    """
    pagination_class = StandardResultsSetPagination
    
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
        
        # فیلتر بر اساس مکان
        facility_id = self.request.query_params.get('facility')
        if facility_id:
            queryset = queryset.filter(facility_id=facility_id)
        
        # فیلتر بر اساس کاربر
        user_only = self.request.query_params.get('user_only')
        if user_only and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        
        # فیلتر بر اساس امتیاز
        rating = self.request.query_params.get('rating')
        if rating:
            try:
                rating_int = int(rating)
                queryset = queryset.filter(rating=rating_int)
            except ValueError:
                pass
        
        # فقط نظرات تایید شده برای کاربران عادی
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        
        return queryset.order_by('-created_at')
    
    def create(self, request):
        """ثبت نظر جدید"""
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
        """ویرایش نظر"""
        try:
            review = self.get_queryset().get(review_id=pk)
            
            # بررسی مالکیت
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
        """حذف نظر"""
        try:
            review = self.get_queryset().get(review_id=pk)
            
            # بررسی مالکیت
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
