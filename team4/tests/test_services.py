"""
Tests for FacilityService
"""
from django.test import TestCase
from team4.models import Province, City, Category, Facility, Amenity, FacilityAmenity
from team4.services.facility_service import FacilityService


class FacilityServiceTest(TestCase):
    """تست سرویس امکانات"""
    
    def setUp(self):
        # ایجاد داده‌های تست
        self.province = Province.objects.create(name_fa="فارس", name_en="Fars")
        self.city = City.objects.create(
            province=self.province,
            name_fa="شیراز",
            name_en="Shiraz",
            latitude=29.591768,
            longitude=52.583698
        )
        self.category_hotel = Category.objects.create(name_fa="هتل", name_en="Hotel")
        self.category_restaurant = Category.objects.create(name_fa="رستوران", name_en="Restaurant")
        
        # ایجاد امکانات
        self.amenity_wifi = Amenity.objects.create(name_fa="وای‌فای", name_en="WiFi")
        self.amenity_parking = Amenity.objects.create(name_fa="پارکینگ", name_en="Parking")
        
        # ایجاد هتل‌ها
        self.hotel1 = Facility.objects.create(
            name_fa="هتل 1",
            name_en="Hotel 1",
            category=self.category_hotel,
            city=self.city,
            address="آدرس 1",
            latitude=29.610000,
            longitude=52.540000,
            avg_rating=4.5,
            review_count=100
        )
        
        self.hotel2 = Facility.objects.create(
            name_fa="هتل 2",
            name_en="Hotel 2",
            category=self.category_hotel,
            city=self.city,
            address="آدرس 2",
            latitude=29.620000,
            longitude=52.550000,
            avg_rating=4.0,
            review_count=50
        )
        
        self.restaurant = Facility.objects.create(
            name_fa="رستوران",
            name_en="Restaurant",
            category=self.category_restaurant,
            city=self.city,
            address="آدرس رستوران",
            latitude=29.605000,
            longitude=52.545000,
            avg_rating=4.7
        )
    
    def test_search_facilities_by_city(self):
        """تست جستجو بر اساس شهر"""
        results = FacilityService.search_facilities(city_name="شیراز")
        self.assertEqual(results.count(), 3)
    
    def test_search_facilities_by_category(self):
        """تست جستجو بر اساس دسته‌بندی"""
        results = FacilityService.search_facilities(category_name="هتل")
        self.assertEqual(results.count(), 2)
    
    def test_search_facilities_combined(self):
        """تست جستجو ترکیبی"""
        results = FacilityService.search_facilities(
            city_name="شیراز",
            category_name="هتل"
        )
        self.assertEqual(results.count(), 2)
    
    def test_filter_by_rating(self):
        """تست فیلتر بر اساس امتیاز"""
        facilities = FacilityService.search_facilities(city_name="شیراز")
        filtered = FacilityService.filter_facilities(
            facilities,
            {'min_rating': 4.5}
        )
        self.assertEqual(filtered.count(), 2)  # hotel1 و restaurant
    
    def test_sort_by_distance(self):
        """تست مرتب‌سازی بر اساس فاصله"""
        facilities = [self.hotel1, self.hotel2, self.restaurant]
        sorted_facilities = FacilityService.sort_by_distance(
            facilities,
            29.591768,  # مرکز شهر
            52.583698
        )
        
        self.assertEqual(len(sorted_facilities), 3)
        # اولین مورد باید نزدیک‌ترین باشه
        self.assertLessEqual(
            sorted_facilities[0]['distance_km'],
            sorted_facilities[1]['distance_km']
        )
    
    def test_get_facility_details(self):
        """تست دریافت جزئیات"""
        facility = FacilityService.get_facility_details(self.hotel1.fac_id)
        self.assertEqual(facility.fac_id, self.hotel1.fac_id)
        self.assertEqual(facility.name_fa, "هتل 1")
    
    def test_get_nearby_facilities(self):
        """تست یافتن امکانات نزدیک"""
        nearby = FacilityService.get_nearby_facilities(
            fac_id=self.hotel1.fac_id,
            radius_km=5
        )
        
        # باید hotel2 و restaurant رو پیدا کنه
        self.assertGreaterEqual(len(nearby), 1)
    
    def test_compare_facilities(self):
        """تست مقایسه امکانات"""
        comparison = FacilityService.compare_facilities([
            self.hotel1.fac_id,
            self.hotel2.fac_id
        ])
        
        self.assertIn('facilities', comparison)
        self.assertEqual(len(comparison['facilities']), 2)
        self.assertIn('comparison_matrix', comparison)
