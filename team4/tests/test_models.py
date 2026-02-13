"""
Unit Tests for Models
"""
from django.test import TestCase
from team4.models import Province, City, Category, Amenity, Facility, Pricing, Image


class ProvinceModelTest(TestCase):
    """تست مدل استان"""
    
    def setUp(self):
        self.province = Province.objects.create(
            name_fa="فارس",
            name_en="Fars"
        )
    
    def test_province_creation(self):
        """تست ایجاد استان"""
        self.assertEqual(self.province.name_fa, "فارس")
        self.assertEqual(self.province.name_en, "Fars")
        self.assertIsNotNone(self.province.province_id)
    
    def test_province_str(self):
        """تست __str__"""
        self.assertEqual(str(self.province), "فارس")


class CityModelTest(TestCase):
    """تست مدل شهر"""
    
    def setUp(self):
        self.province = Province.objects.create(name_fa="فارس", name_en="Fars")
        self.city = City.objects.create(
            province=self.province,
            name_fa="شیراز",
            name_en="Shiraz",
            latitude=29.591768,
            longitude=52.583698
        )
    
    def test_city_creation(self):
        """تست ایجاد شهر"""
        self.assertEqual(self.city.name_fa, "شیراز")
        self.assertEqual(self.city.province, self.province)
    
    def test_city_location(self):
        """تست دریافت موقعیت"""
        location = self.city.get_location()
        self.assertEqual(len(location), 2)
        self.assertIsInstance(location[0], float)


class FacilityModelTest(TestCase):
    """تست مدل مکان"""
    
    def setUp(self):
        self.province = Province.objects.create(name_fa="فارس", name_en="Fars")
        self.city = City.objects.create(
            province=self.province,
            name_fa="شیراز",
            name_en="Shiraz",
            latitude=29.591768,
            longitude=52.583698
        )
        self.category = Category.objects.create(
            name_fa="هتل",
            name_en="Hotel"
        )
        self.facility = Facility.objects.create(
            name_fa="هتل تست",
            name_en="Test Hotel",
            category=self.category,
            city=self.city,
            address="آدرس تست",
            latitude=29.610000,
            longitude=52.540000
        )
    
    def test_facility_creation(self):
        """تست ایجاد مکان"""
        self.assertEqual(self.facility.name_fa, "هتل تست")
        self.assertEqual(self.facility.category, self.category)
        self.assertEqual(self.facility.avg_rating, 0)
    
    def test_calculate_distance(self):
        """تست محاسبه فاصله"""
        distance = self.facility.calculate_distance_to(29.62, 52.55)
        self.assertGreater(distance, 0)
        self.assertIsInstance(distance, float)
    
    def test_get_location(self):
        """تست دریافت موقعیت"""
        location = self.facility.get_location()
        self.assertEqual(len(location), 2)


class PricingModelTest(TestCase):
    """تست مدل قیمت"""
    
    def setUp(self):
        province = Province.objects.create(name_fa="فارس", name_en="Fars")
        city = City.objects.create(
            province=province,
            name_fa="شیراز",
            name_en="Shiraz",
            latitude=29.591768,
            longitude=52.583698
        )
        category = Category.objects.create(name_fa="هتل", name_en="Hotel")
        self.facility = Facility.objects.create(
            name_fa="هتل تست",
            name_en="Test Hotel",
            category=category,
            city=city,
            address="آدرس تست",
            latitude=29.610000,
            longitude=52.540000
        )
        self.pricing = Pricing.objects.create(
            facility=self.facility,
            price_type='Per Night',
            price=1200000,
            description_fa="اتاق دو تخته"
        )
    
    def test_pricing_creation(self):
        """تست ایجاد قیمت"""
        self.assertEqual(self.pricing.facility, self.facility)
        self.assertEqual(self.pricing.price, 1200000)
    
    def test_get_min_price(self):
        """تست دریافت کمترین قیمت"""
        min_price = self.facility.get_min_price()
        self.assertEqual(min_price, 1200000)
