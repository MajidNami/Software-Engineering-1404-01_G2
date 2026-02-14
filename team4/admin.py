from django.contrib import admin
from team4.models import (
    Province, City,Village, Category, Amenity,
    Facility, FacilityAmenity, Pricing, Image,
    Favorite, Review
)


# =====================================================
# Inline Admins
# =====================================================

class VillageInline(admin.TabularInline):
    model = Village
    extra = 1
    fields = ['name_fa', 'name_en', 'location']

class PricingInline(admin.TabularInline):
    model = Pricing
    extra = 1
    fields = ['price_type', 'price', 'description_fa', 'status']


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ['image_url', 'is_primary', 'alt_text']


class FacilityAmenityInline(admin.TabularInline):
    model = FacilityAmenity
    extra = 1


# =====================================================
# Model Admins
# =====================================================

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['province_id', 'name_fa', 'name_en', 'created_at']
    search_fields = ['name_fa', 'name_en']
    list_filter = ['created_at']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['city_id', 'name_fa', 'province', 'latitude', 'longitude']
    search_fields = ['name_fa', 'name_en']
    list_filter = ['province', 'created_at']
    autocomplete_fields = ['province']
    inlines = [VillageInline]

@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ['village_id', 'name_fa', 'city', 'latitude', 'longitude', 'created_at']
    search_fields = ['name_fa', 'name_en']
    list_filter = ['city', 'created_at']
    autocomplete_fields = ['city'] # Enables search for City in dropdowns


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'name_fa', 'name_en', 'is_emergency', 'marker_color']
    search_fields = ['name_fa', 'name_en']
    list_filter = ['is_emergency', 'marker_color']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['amenity_id', 'name_fa', 'name_en', 'icon']
    search_fields = ['name_fa', 'name_en']


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = [
        'fac_id', 'name_fa', 'city', 'category',
        'avg_rating', 'review_count', 'status', 'is_24_hour'
    ]
    search_fields = ['name_fa', 'name_en', 'address']
    list_filter = ['category', 'city', 'status', 'is_24_hour', 'created_at']
    autocomplete_fields = ['city', 'category']
    
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('name_fa', 'name_en', 'category', 'city')
        }),
        ('موقعیت', {
            'fields': ('address', 'location')
        }),
        ('تماس', {
            'fields': ('phone', 'email', 'website')
        }),
        ('توضیحات', {
            'fields': ('description_fa', 'description_en')
        }),
        ('امتیاز و نظرات', {
            'fields': ('avg_rating', 'review_count')
        }),
        ('وضعیت', {
            'fields': ('status', 'is_24_hour')
        }),
    )
    
    inlines = [PricingInline, ImageInline, FacilityAmenityInline]
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    list_display = ['pricing_id', 'facility', 'price_type', 'price', 'status']
    search_fields = ['facility__name_fa']
    list_filter = ['price_type', 'status', 'created_at']
    autocomplete_fields = ['facility']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['image_id', 'facility', 'is_primary', 'uploaded_at']
    search_fields = ['facility__name_fa', 'alt_text']
    list_filter = ['is_primary', 'uploaded_at']
    autocomplete_fields = ['facility']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['favorite_id', 'user', 'facility', 'created_at']
    search_fields = ['user__email', 'facility__name_fa', 'facility__name_en']
    list_filter = ['created_at']
    autocomplete_fields = ['facility']
    date_hierarchy = 'created_at'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ['user', 'facility', 'created_at']
        return ['created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'user', 'facility', 'rating', 'is_approved', 'created_at']
    search_fields = ['user__email', 'facility__name_fa', 'facility__name_en', 'comment']
    list_filter = ['rating', 'is_approved', 'created_at']
    autocomplete_fields = ['facility']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'facility', 'rating')
        }),
        ('نظر', {
            'fields': ('comment', 'is_approved')
        }),
        ('تاریخ', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        for review in queryset:
            review.update_facility_rating()
    approve_reviews.short_description = "تایید نظرات انتخاب شده"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        for review in queryset:
            review.update_facility_rating()
    disapprove_reviews.short_description = "رد نظرات انتخاب شده"

