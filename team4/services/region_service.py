from django.db.models import Q
from team4.models import Province, City, Village


class RegionService:
    """سرویس برای مدیریت جستجوی مناطق (استان، شهر، روستا)"""
    
    @staticmethod
    def search_regions(query, region_type=None):
        """
        جستجوی مناطق بر اساس نوع
        
        Args:
            query: متن جستجو
            region_type: نوع منطقه - 'province', 'city', 'village' (اختیاری)
            
        Returns:
            list: لیست دیکشنری‌های حاوی اطلاعات منطقه
        """
        if not query:
            return []
        
        results = []
        
        # جستجو در استان‌ها
        if not region_type or region_type == 'province':
            results.extend(RegionService._search_provinces(query))
        
        # جستجو در شهرها
        if not region_type or region_type == 'city':
            results.extend(RegionService._search_cities(query))
        
        # جستجو در روستاها
        if not region_type or region_type == 'village':
            results.extend(RegionService._search_villages(query))
        
        return results
    
    @staticmethod
    def _search_provinces(query):
        """جستجوی استان‌ها"""
        provinces = Province.objects.filter(
            Q(name_fa__icontains=query) | 
            Q(name_en__icontains=query)
        )
        
        return [{
            'id': str(province.province_id),
            'name': province.name_fa,
            'parent_region_id': None,
            'parent_region_name': None
        } for province in provinces]
    
    @staticmethod
    def _search_cities(query):
        """جستجوی شهرها"""
        cities = City.objects.select_related('province').filter(
            Q(name_fa__icontains=query) | 
            Q(name_en__icontains=query)
        )
        
        return [{
            'id': str(city.city_id),
            'name': city.name_fa,
            'parent_region_id': str(city.province.province_id),
            'parent_region_name': city.province.name_fa
        } for city in cities]
    
    @staticmethod
    def _search_villages(query):
        """جستجوی روستاها"""
        villages = Village.objects.select_related('city', 'city__province').filter(
            Q(name_fa__icontains=query) | 
            Q(name_en__icontains=query)
        )
        
        return [{
            'id': str(village.village_id),
            'name': village.name_fa,
            'parent_region_id': str(village.city.city_id),
            'parent_region_name': village.city.name_fa
        } for village in villages]
    
    @staticmethod
    def validate_region_type(region_type):
        """
        اعتبارسنجی نوع منطقه
        
        Returns:
            tuple: (is_valid, error_message)
        """
        valid_types = ['province', 'city', 'village']
        
        if not region_type:
            return True, None
        
        if region_type not in valid_types:
            return False, f'region_type باید یکی از مقادیر {valid_types} باشد'
        
        return True, None
