from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from .fields import PointField, Point
import math


# RegionType Enum
class RegionType(models.TextChoices):
    PROVINCE = 'province', 'استان'
    CITY = 'city', 'شهر'
    VILLAGE = 'village', 'روستا'


# PriceTier Enum
class PriceTier(models.TextChoices):
    UNKNOWN = 'unknown', 'نامشخص'
    FREE = 'free', 'رایگان'
    BUDGET = 'budget', 'اقتصادی'
    MODERATE = 'moderate', 'متوسط'
    EXPENSIVE = 'expensive', 'گران'
    LUXURY = 'luxury', 'لوکس'



class Province(models.Model):
    province_id = models.AutoField(primary_key=True)
    name_fa = models.CharField(max_length=100, verbose_name="نام فارسی")
    name_en = models.CharField(max_length=100, unique=True, verbose_name="نام انگلیسی")
    location = PointField(null=True, blank=True, verbose_name="موقعیت جغرافیایی مرکز")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities_province'
        verbose_name = "استان"
        verbose_name_plural = "استان‌ها"
        indexes = [
            models.Index(fields=['name_en'], name='idx_province_name_en'),
        ]

    def __str__(self):
        return self.name_fa

    def clean(self):
        if len(self.name_en) <= 1:
            raise ValidationError("نام انگلیسی باید بیشتر از یک کاراکتر باشد")
    
    def get_coordinates(self):
        if self.location:
            return (self.location.longitude, self.location.latitude)
        return None
    
    @property
    def latitude(self):
        return self.location.latitude if self.location else None
    
    @property
    def longitude(self):
        return self.location.longitude if self.location else None


class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name="استان"
    )
    name_fa = models.CharField(max_length=100, verbose_name="نام فارسی")
    name_en = models.CharField(max_length=100, verbose_name="نام انگلیسی")
    location = PointField(verbose_name="موقعیت جغرافیایی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities_city'
        verbose_name = "شهر"
        verbose_name_plural = "شهرها"
        unique_together = [['province', 'name_en']]
        indexes = [
            models.Index(fields=['province'], name='idx_city_province'),
        ]

    def __str__(self):
        return f"{self.name_fa} ({self.province.name_fa})"

    def get_coordinates(self):
        if self.location:
            return (self.location.longitude, self.location.latitude)
        return None
    
    @property
    def latitude(self):
        return self.location.latitude if self.location else None
    
    @property
    def longitude(self):
        return self.location.longitude if self.location else None


class Village(models.Model):
    village_id = models.AutoField(primary_key=True)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='villages',
        verbose_name="شهر"
    )
    name_fa = models.CharField(max_length=100, verbose_name="نام فارسی")
    name_en = models.CharField(max_length=100, verbose_name="نام انگلیسی")
    location = PointField(null=True, blank=True, verbose_name="موقعیت جغرافیایی")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities_village'
        verbose_name = "روستا"
        verbose_name_plural = "روستاها"
        unique_together = [['city', 'name_en']]
        indexes = [
            models.Index(fields=['city'], name='idx_village_city'),
            models.Index(fields=['name_en'], name='idx_village_name_en'),
        ]

    def __str__(self):
        return f"{self.name_fa} ({self.city.name_fa})"

    def get_coordinates(self):
        if self.location:
            return (self.location.longitude, self.location.latitude)
        return None
    
    @property
    def latitude(self):
        return self.location.latitude if self.location else None
    
    @property
    def longitude(self):
        return self.location.longitude if self.location else None


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name_fa = models.CharField(max_length=100, verbose_name="نام فارسی")
    name_en = models.CharField(max_length=100, unique=True, verbose_name="نام انگلیسی")
    is_emergency = models.BooleanField(default=False, verbose_name="خدمات اضطراری")
    marker_color = models.CharField(
        max_length=20, 
        default='blue',
        choices=[
            ('blue', 'آبی'),
            ('red', 'قرمز'),
            ('green', 'سبز'),
            ('orange', 'نارنجی'),
            ('purple', 'بنفش'),
            ('yellow', 'زرد'),
        ],
        verbose_name="رنگ نشانگر"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities_category'
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        indexes = [
            models.Index(fields=['name_en'], name='idx_category_name'),
        ]

    def __str__(self):
        return self.name_fa


class Amenity(models.Model):
    amenity_id = models.AutoField(primary_key=True)
    name_fa = models.CharField(max_length=100, verbose_name="نام فارسی")
    name_en = models.CharField(max_length=100, unique=True, verbose_name="نام انگلیسی")
    icon = models.CharField(max_length=50, blank=True, verbose_name="آیکون")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities_amenity'
        verbose_name = "امکانات"
        verbose_name_plural = "امکانات"

    def __str__(self):
        return self.name_fa


class Facility(models.Model):
    fac_id = models.BigAutoField(primary_key=True)
    name_fa = models.CharField(max_length=200, verbose_name="نام فارسی")
    name_en = models.CharField(max_length=200, verbose_name="نام انگلیسی")
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='facilities',
        verbose_name="دسته‌بندی"
    )
    city = models.ForeignKey(
        City,
        on_delete=models.RESTRICT,
        related_name='facilities',
        verbose_name="شهر"
    )
    
    address = models.TextField(verbose_name="آدرس")
    location = PointField(verbose_name="موقعیت جغرافیایی") 
    phone = models.CharField(max_length=20, blank=True, verbose_name="تلفن")
    email = models.EmailField(blank=True, validators=[EmailValidator()], verbose_name="ایمیل")
    website = models.URLField(max_length=200, blank=True, verbose_name="وبسایت")
    description_fa = models.TextField(blank=True, verbose_name="توضیحات فارسی")
    description_en = models.TextField(blank=True, verbose_name="توضیحات انگلیسی")
    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="امتیاز میانگین"
    )
    review_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="تعداد نظرات"
    )
    
    status = models.BooleanField(default=True, verbose_name="وضعیت فعال")
    is_24_hour = models.BooleanField(default=False, verbose_name="24 ساعته")
    
    price_tier = models.CharField(
        max_length=20,
        choices=PriceTier.choices,
        default=PriceTier.UNKNOWN,
        verbose_name="سطح قیمت"
    )
    
    amenities = models.ManyToManyField(
        Amenity,
        through='FacilityAmenity',
        related_name='facilities',
        blank=True,
        verbose_name="امکانات"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities_facility'
        verbose_name = "مکان"
        verbose_name_plural = "مکان‌ها"
        unique_together = [['name_en', 'city']]
        indexes = [
            models.Index(fields=['category'], name='idx_facility_category'),
            models.Index(fields=['city'], name='idx_facility_city'),
            models.Index(fields=['status'], name='idx_facility_status'),
        ]

    def __str__(self):
        return f"{self.name_fa} - {self.city.name_fa}"

    def get_coordinates(self):
        if self.location:
            return (self.location.longitude, self.location.latitude)
        return None
    
    @property
    def latitude(self):
        return self.location.latitude if self.location else None
    
    @property
    def longitude(self):
        return self.location.longitude if self.location else None

    def calculate_distance_to(self, point):
        """محاسبه فاصله تا یک نقطه - برحسب کیلومتر
        
        Args:
            point: Point object یا tuple (lng, lat)
        
        Returns:
            float: فاصله به کیلومتر
        """
        if not self.location:
            return None
        
        # اگر tuple بود، تبدیل به Point کن
        if isinstance(point, (tuple, list)):
            point = Point(point[0], point[1])
        
        # محاسبه فاصله با استفاده از Haversine formula
        return self.location.distance(point)

    def get_primary_image(self):
        return self.images.filter(is_primary=True).first()

    def get_min_price(self):
        """دریافت کمترین قیمت - اگر قیمت دقیق نداشت، بر اساس tier تخمین میزنه"""
        pricing = self.pricing_set.filter(status=True).order_by('price').first()
        if pricing:
            return pricing.price
        
        # اگر قیمت دقیق نداشت، بر اساس tier یه range برمیگردونه
        return None
    
    def get_price_tier_display_range(self):
        """بازه تقریبی قیمت بر اساس tier (به تومان)"""
        tier_ranges = {
            PriceTier.FREE: (0, 0),
            PriceTier.BUDGET: (100_000, 500_000),
            PriceTier.MODERATE: (500_000, 1_500_000),
            PriceTier.EXPENSIVE: (1_500_000, 3_000_000),
            PriceTier.LUXURY: (3_000_000, 10_000_000),
            PriceTier.UNKNOWN: (None, None),
        }
        return tier_ranges.get(self.price_tier, (None, None))


class FacilityAmenity(models.Model):
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        verbose_name="مکان"
    )
    amenity = models.ForeignKey(
        Amenity,
        on_delete=models.CASCADE,
        verbose_name="امکانات"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities_facility_amenity'
        unique_together = [['facility', 'amenity']]
        verbose_name = "امکانات مکان"
        verbose_name_plural = "امکانات مکان‌ها"
        indexes = [
            models.Index(fields=['facility'], name='idx_fac_amenity_fac'),
            models.Index(fields=['amenity'], name='idx_fac_amenity_amenity'),
        ]

    def __str__(self):
        return f"{self.facility.name_fa} - {self.amenity.name_fa}"


class Pricing(models.Model):
    PRICE_TYPE_CHOICES = [
        ('Hourly', 'ساعتی'),
        ('Daily', 'روزانه'),
        ('Monthly', 'ماهانه'),
        ('Per Night', 'هر شب'),
        ('Per Session', 'هر جلسه'),
    ]
    
    pricing_id = models.BigAutoField(primary_key=True)
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='pricing_set',
        verbose_name="مکان"
    )
    price_type = models.CharField(
        max_length=50,
        choices=PRICE_TYPE_CHOICES,
        verbose_name="نوع قیمت"
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="قیمت (تومان)"
    )
    description_fa = models.TextField(blank=True, verbose_name="توضیحات فارسی")
    description_en = models.TextField(blank=True, verbose_name="توضیحات انگلیسی")
    status = models.BooleanField(default=True, verbose_name="وضعیت فعال")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities_pricing'
        verbose_name = "قیمت"
        verbose_name_plural = "قیمت‌ها"
        indexes = [
            models.Index(fields=['facility'], name='idx_pricing_fac'),
        ]

    def __str__(self):
        return f"{self.facility.name_fa} - {self.get_price_type_display()}: {self.price:,} تومان"


class Image(models.Model):
    image_id = models.BigAutoField(primary_key=True)
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="مکان"
    )
    image_url = models.URLField(max_length=500, verbose_name="URL تصویر")
    is_primary = models.BooleanField(default=False, verbose_name="تصویر اصلی")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="متن جایگزین")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'facilities_image'
        verbose_name = "تصویر"
        verbose_name_plural = "تصاویر"
        indexes = [
            models.Index(fields=['facility'], name='idx_image_fac'),
            models.Index(fields=['facility', 'is_primary'], name='idx_image_primary'),
        ]

    def __str__(self):
        return f"{self.facility.name_fa} - {'اصلی' if self.is_primary else 'جانبی'}"

    def clean(self):
        if not self.image_url:
            raise ValidationError("URL تصویر نمی‌تواند خالی باشد")


class Favorite(models.Model):
    """مدل علاقه‌مندی‌ها - ذخیره مکان‌های مورد علاقه کاربران"""
    favorite_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="کاربر"
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name="مکان"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ افزودن")

    class Meta:
        db_table = 'facilities_favorite'
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"
        unique_together = [['user', 'facility']]
        indexes = [
            models.Index(fields=['user'], name='idx_favorite_user'),
            models.Index(fields=['facility'], name='idx_favorite_facility'),
            models.Index(fields=['-created_at'], name='idx_favorite_created'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.facility.name_fa}"


class Review(models.Model):
    """مدل نظرات - نظرات و امتیازات کاربران برای مکان‌ها"""
    review_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="کاربر"
    )
    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="مکان"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="امتیاز"
    )
    comment = models.TextField(blank=True, verbose_name="نظر")
    is_approved = models.BooleanField(default=True, verbose_name="تایید شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        db_table = 'facilities_review'
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"
        unique_together = [['user', 'facility']]
        indexes = [
            models.Index(fields=['user'], name='idx_review_user'),
            models.Index(fields=['facility'], name='idx_review_facility'),
            models.Index(fields=['-created_at'], name='idx_review_created'),
            models.Index(fields=['is_approved'], name='idx_review_approved'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.facility.name_fa} ({self.rating}★)"

    def clean(self):
        if self.rating < 1 or self.rating > 5:
            raise ValidationError("امتیاز باید بین 1 تا 5 باشد")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # بروزرسانی امتیاز میانگین و تعداد نظرات مکان
        self.update_facility_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        # بروزرسانی امتیاز میانگین و تعداد نظرات مکان
        self.update_facility_rating()

    def update_facility_rating(self):
        """بروزرسانی امتیاز میانگین و تعداد نظرات مکان"""
        from django.db.models import Avg, Count
        
        # محاسبه امتیاز میانگین و تعداد نظرات تایید شده
        stats = Review.objects.filter(
            facility=self.facility,
            is_approved=True
        ).aggregate(
            avg_rating=Avg('rating'),
            review_count=Count('review_id')
        )
        
        # بروزرسانی مکان
        self.facility.avg_rating = stats['avg_rating'] or 0.00
        self.facility.review_count = stats['review_count'] or 0
        self.facility.save(update_fields=['avg_rating', 'review_count'])
