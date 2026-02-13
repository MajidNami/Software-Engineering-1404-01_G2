from django.db.models import Q, F, Count, Min, Avg
from django.core.exceptions import ObjectDoesNotExist
from ..fields import Point
from team4.models import Facility, City, Category, Amenity, Pricing


class FacilityService:
    
    @staticmethod
    def search_facilities(city_name=None, category_name=None, **filters):
        queryset = Facility.objects.filter(status=True)
        
        # فیلتر شهر
        if city_name:
            queryset = queryset.filter(
                Q(city__name_fa__icontains=city_name) | 
                Q(city__name_en__icontains=city_name)
            )
        
        # فیلتر دسته‌بندی
        if category_name:
            queryset = queryset.filter(
                Q(category__name_fa__icontains=category_name) | 
                Q(category__name_en__icontains=category_name)
            )
        
        # Select Related برای بهینه‌سازی
        queryset = queryset.select_related('city', 'city__province', 'category')
        queryset = queryset.prefetch_related('amenities', 'pricing_set', 'images')
        
        return queryset
    
    @staticmethod
    def filter_facilities(queryset, filters):
        min_price = filters.get('min_price')
        max_price = filters.get('max_price')
        
        if min_price or max_price:
            facility_ids = Pricing.objects.filter(status=True)
            
            if min_price:
                facility_ids = facility_ids.filter(price__gte=min_price)
            if max_price:
                facility_ids = facility_ids.filter(price__lte=max_price)
            
            facility_ids = facility_ids.values_list('facility_id', flat=True).distinct()
            queryset = queryset.filter(fac_id__in=facility_ids)
        
        # فیلتر امتیاز
        min_rating = filters.get('min_rating')
        if min_rating:
            queryset = queryset.filter(avg_rating__gte=min_rating)
        
        # فیلتر امکانات
        amenities = filters.get('amenities')
        if amenities:
            # amenities می‌تونه لیست یا string کاما-separated باشه
            if isinstance(amenities, str):
                amenities = [int(x.strip()) for x in amenities.split(',') if x.strip()]
            
            for amenity_id in amenities:
                queryset = queryset.filter(amenities__amenity_id=amenity_id)
        
        # فیلتر 24 ساعته
        is_24_hour = filters.get('is_24_hour')
        if is_24_hour in [True, 'true', 'True', '1']:
            queryset = queryset.filter(is_24_hour=True)
        
        return queryset.distinct()
    
    @staticmethod
    def sort_by_distance(facilities, reference_point):
        # تبدیل به Point اگر tuple است
        if isinstance(reference_point, (tuple, list)):
            reference_point = Point(reference_point[0], reference_point[1], srid=4326)
        
        facilities_with_distance = []
        
        for facility in facilities:
            distance = facility.calculate_distance_to(reference_point)
            if distance is not None:
                facilities_with_distance.append({
                    'facility': facility,
                    'distance_km': round(distance, 2)
                })
        
        # مرتب‌سازی بر اساس فاصله
        facilities_with_distance.sort(key=lambda x: x['distance_km'])
        
        return facilities_with_distance
    
    @staticmethod
    def get_facility_details(fac_id):
        try:
            facility = Facility.objects.select_related(
                'city', 'city__province', 'category'
            ).prefetch_related(
                'amenities',
                'pricing_set',
                'images'
            ).get(fac_id=fac_id, status=True)
            
            return facility
        except Facility.DoesNotExist:
            raise ObjectDoesNotExist(f"مکان با شناسه {fac_id} یافت نشد")
    
    @staticmethod
    def get_nearby_facilities(fac_id, radius_km=5, category_name=None):
        """
        دریافت امکانات نزدیک
        
        Returns:
            tuple: (center_facility, nearby_facilities_list)
                   اگر مکان مرکزی یافت نشد: (None, [])
                   اگر location نداشت: (center_facility, [])
        """
        try:
            center_facility = Facility.objects.select_related(
                'city', 'category'
            ).prefetch_related('amenities').get(fac_id=fac_id)
        except Facility.DoesNotExist:
            return None, []
        
        if not center_facility.location:
            return center_facility, []
        
        # دریافت تمام امکانات (به جز خود مکان مرجع)
        nearby = Facility.objects.filter(status=True).exclude(fac_id=fac_id)
        
        # فیلتر دسته‌بندی
        if category_name:
            nearby = nearby.filter(
                Q(category__name_fa__icontains=category_name) | 
                Q(category__name_en__icontains=category_name)
            )
        
        nearby = nearby.select_related('city', 'category').prefetch_related('amenities')
        
        # محاسبه فاصله و فیلتر
        nearby_with_distance = []
        
        for facility in nearby:
            if not facility.location:
                continue
                
            distance = facility.calculate_distance_to(center_facility.location)
            
            if distance and distance <= radius_km:
                # محاسبه زمان پیاده‌روی (فرض: 5 km/h)
                walking_time = round((distance / 5) * 60)  # دقیقه
                
                nearby_with_distance.append({
                    'facility': facility,
                    'distance_km': round(distance, 2),
                    'walking_time_minutes': walking_time,
                    'driving_time_minutes': None  # باید از Neshan API بگیریم
                })
        
        # مرتب‌سازی بر اساس فاصله
        nearby_with_distance.sort(key=lambda x: x['distance_km'])
        
        return center_facility, nearby_with_distance
    
    @staticmethod
    def compare_facilities(fac_ids):
        if not fac_ids or len(fac_ids) < 2:
            return {'error': 'حداقل 2 مکان برای مقایسه لازم است'}
        
        if len(fac_ids) > 5:
            return {'error': 'حداکثر 5 مکان قابل مقایسه است'}
        
        facilities = Facility.objects.filter(
            fac_id__in=fac_ids,
            status=True
        ).select_related(
            'city', 'category'
        ).prefetch_related(
            'amenities', 'pricing_set', 'images'
        )
        
        if not facilities:
            return {'error': 'هیچ مکانی یافت نشد'}
        
        # آماده‌سازی داده برای مقایسه
        comparison_data = []
        all_amenities = set()
        lowest_price_id = None
        lowest_price = float('inf')
        highest_rating_id = None
        highest_rating = 0
        most_amenities_id = None
        most_amenities_count = 0
        
        for facility in facilities:
            # دریافت کمترین قیمت
            min_price_obj = facility.pricing_set.filter(status=True).order_by('price').first()
            min_price = float(min_price_obj.price) if min_price_obj else 0
            
            # آپدیت کمترین قیمت
            if min_price > 0 and min_price < lowest_price:
                lowest_price = min_price
                lowest_price_id = facility.fac_id
            
            # آپدیت بالاترین امتیاز
            if float(facility.avg_rating) > highest_rating:
                highest_rating = float(facility.avg_rating)
                highest_rating_id = facility.fac_id
            
            # دریافت امکانات
            facility_amenities = facility.amenities.all()
            amenity_count = facility_amenities.count()
            
            if amenity_count > most_amenities_count:
                most_amenities_count = amenity_count
                most_amenities_id = facility.fac_id
            
            # اضافه کردن به لیست کل امکانات
            for amenity in facility_amenities:
                all_amenities.add(amenity.name_en)
            
            # محاسبه فاصله از مرکز شهر
            distance_from_center = 0
            if facility.city.location and facility.location:
                distance_from_center = facility.calculate_distance_to(facility.city.location)
            
            # ساخت دیکشنری امکانات
            amenities_dict = {amenity.name_en: True for amenity in facility_amenities}
            
            comparison_data.append({
                'fac_id': facility.fac_id,
                'name_fa': facility.name_fa,
                'image_url': facility.get_primary_image().image_url if facility.get_primary_image() else None,
                'avg_rating': float(facility.avg_rating),
                'price_per_night': min_price,
                'distance_from_center_km': round(distance_from_center, 2),
                'amenities': amenities_dict,
                'amenities_list': [a.name_fa for a in facility_amenities],
                'review_count': facility.review_count,
                'is_24_hour': facility.is_24_hour,
            })
        
        return {
            'facilities': comparison_data,
            'all_amenities': sorted(list(all_amenities)),
            'comparison_matrix': {
                'lowest_price': lowest_price_id,
                'highest_rating': highest_rating_id,
                'most_amenities': most_amenities_id,
            }
        }
    
    @staticmethod
    def sort_by_city_distance(facilities, city_name):
        """
        مرتب‌سازی امکانات بر اساس فاصله از مرکز شهر
        
        Args:
            facilities: QuerySet یا لیست امکانات
            city_name: نام شهر
            
        Returns:
            list یا None: لیست امکانات مرتب شده یا None اگر شهر یافت نشد
        """
        city = City.objects.filter(
            Q(name_fa__icontains=city_name) | 
            Q(name_en__icontains=city_name)
        ).first()
        
        if not city or not city.location:
            return None
        
        facilities_list = list(facilities)
        return FacilityService.sort_by_distance(facilities_list, city.location)
    
    @staticmethod
    def validate_radius(radius_value):
        """
        اعتبارسنجی شعاع جستجو
        
        Returns:
            tuple: (is_valid, radius_float, error_message)
        """
        try:
            radius = float(radius_value)
            if radius <= 0 or radius > 100:
                return False, None, 'radius باید عدد بین 1 تا 100 باشد'
            return True, radius, None
        except (ValueError, TypeError):
            return False, None, 'radius باید یک عدد معتبر باشد'
    
    @staticmethod
    def get_all_cities():
        return City.objects.select_related('province').all()
    
    @staticmethod
    def get_all_categories():
        return Category.objects.all()
    
    @staticmethod
    def get_all_amenities():
        return Amenity.objects.all()
