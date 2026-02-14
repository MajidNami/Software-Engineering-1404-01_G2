from rest_framework import serializers
from .fields import Point
from team4.models import (
    Province, City, Category, Amenity, Village,
    Facility, FacilityAmenity, Pricing, Image,
    Favorite, Review
)


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['province_id', 'name_fa', 'name_en']


class CitySerializer(serializers.ModelSerializer):
    province = ProvinceSerializer(read_only=True)
    location = serializers.SerializerMethodField()
    
    class Meta:
        model = City
        fields = [
            'city_id', 'name_fa', 'name_en',
            'province', 'location'
        ]
    
    def get_location(self, obj):
        return {
            'type': 'Point',
            'coordinates': [float(obj.longitude), float(obj.latitude)]
        }


class CategorySerializer(serializers.ModelSerializer):    
    class Meta:
        model = Category
        fields = [
            'category_id', 'name_fa', 'name_en',
            'is_emergency', 'marker_color'
        ]


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['amenity_id', 'name_fa', 'name_en', 'icon']


class SimpleAmenitySerializer(serializers.Serializer):
    """Simplified amenity serializer showing just names"""
    name_fa = serializers.CharField()
    name_en = serializers.CharField()


class PricingSerializer(serializers.ModelSerializer):
    price_type_display = serializers.CharField(source='get_price_type_display', read_only=True)
    
    class Meta:
        model = Pricing
        fields = [
            'pricing_id', 'price_type', 'price_type_display',
            'price', 'description_fa', 'description_en', 'status'
        ]


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = [
            'image_id', 'image_url', 'is_primary', 'alt_text'
        ]




class FacilityListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name_en', read_only=True)
    city = serializers.CharField(source='city.name_fa', read_only=True)
    province = serializers.CharField(source='city.province.name_fa', read_only=True)
    location = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    price_from = serializers.SerializerMethodField()
    price_tier = serializers.CharField(read_only=True)
    price_tier_display = serializers.CharField(source='get_price_tier_display', read_only=True)
    amenities = serializers.SerializerMethodField()
    
    class Meta:
        model = Facility
        fields = [
            'fac_id', 'name_fa', 'name_en',
            'category', 'city', 'province', 'location',
            'avg_rating', 'review_count',
            'primary_image', 'price_from', 'price_tier', 'price_tier_display',
            'is_24_hour', 'amenities'
        ]
    
    def get_location(self, obj):
        if obj.location:
            return {
                'type': 'Point',
                'coordinates': [obj.location.longitude, obj.location.latitude]  # [lng, lat]
            }
        return None
    
    def get_primary_image(self, obj):
        image = obj.get_primary_image()
        return image.image_url if image else None
    
    def get_price_from(self, obj):
        """Get minimum price or tier range"""
        min_price = obj.get_min_price()
        if min_price:
            return {
                'type': 'exact',
                'value': float(min_price)
            }
        
        # If no exact price, return tier range
        tier_range = obj.get_price_tier_display_range()
        if tier_range[0] is not None:
            return {
                'type': 'range',
                'min': tier_range[0],
                'max': tier_range[1]
            }
        
        return None
    
    def get_amenities(self, obj):
        """Return list of amenities with just fa and en names"""
        return SimpleAmenitySerializer(obj.amenities.all(), many=True).data


class FacilityDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    city = CitySerializer(read_only=True)
    location = serializers.SerializerMethodField()
    amenities = AmenitySerializer(many=True, read_only=True)
    pricing = PricingSerializer(source='pricing_set', many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    price_tier = serializers.CharField(read_only=True)
    price_tier_display = serializers.CharField(source='get_price_tier_display', read_only=True)
    
    class Meta:
        model = Facility
        fields = [
            'fac_id', 'name_fa', 'name_en',
            'category', 'city', 'address', 'location',
            'phone', 'email', 'website',
            'description_fa', 'description_en',
            'avg_rating', 'review_count',
            'status', 'is_24_hour', 'price_tier', 'price_tier_display',
            'amenities', 'pricing', 'images',
            'created_at', 'updated_at'
        ]
    
    def get_location(self, obj):
        if obj.location:
            return {
                'type': 'Point',
                'coordinates': [obj.location.longitude, obj.location.latitude]  # [lng, lat]
            }
        return None


class FacilityNearbySerializer(serializers.Serializer):
    facility = FacilityListSerializer()
    distance_km = serializers.FloatField()
    walking_time_minutes = serializers.IntegerField()
    driving_time_minutes = serializers.IntegerField(allow_null=True)


class NearbyPlaceSerializer(serializers.Serializer):
    """Serializer for nearby places with distance in meters"""
    place = FacilityListSerializer(source='facility')
    distance_meters = serializers.FloatField()


class FacilityComparisonSerializer(serializers.Serializer):
    fac_id = serializers.IntegerField()
    name_fa = serializers.CharField()
    image_url = serializers.URLField(allow_null=True)
    avg_rating = serializers.FloatField()
    price_per_night = serializers.FloatField()
    distance_from_center_km = serializers.FloatField()
    amenities = serializers.DictField()
    amenities_list = serializers.ListField()
    review_count = serializers.IntegerField()
    is_24_hour = serializers.BooleanField()


# =====================================================
# Create/Update Serializers
# =====================================================

class FacilityCreateSerializer(serializers.ModelSerializer):
    amenity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    
    class Meta:
        model = Facility
        fields = [
            'name_fa', 'name_en',
            'category', 'city',
            'address', 'latitude', 'longitude',
            'phone', 'email', 'website',
            'description_fa', 'description_en',
            'is_24_hour', 'amenity_ids'
        ]
    
    def create(self, validated_data):
        amenity_ids = validated_data.pop('amenity_ids', [])
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        
        # ساخت Point از lat/lng
        validated_data['location'] = Point(longitude, latitude, srid=4326)
        
        facility = Facility.objects.create(**validated_data)
        
        # اضافه کردن امکانات
        if amenity_ids:
            for amenity_id in amenity_ids:
                try:
                    amenity = Amenity.objects.get(amenity_id=amenity_id)
                    FacilityAmenity.objects.create(facility=facility, amenity=amenity)
                except Amenity.DoesNotExist:
                    pass
        
        return facility


# =====================================================
# Region Search Serializers
# =====================================================

class VillageSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    location = serializers.SerializerMethodField()
    
    class Meta:
        model = Village
        fields = [
            'village_id', 'name_fa', 'name_en',
            'city', 'location'
        ]
    
    def get_location(self, obj):
        if obj.location:
            return {
                'type': 'Point',
                'coordinates': [float(obj.longitude), float(obj.latitude)]
            }
        return None


class RegionSearchResultSerializer(serializers.Serializer):
    """سریالایزر برای نتایج جستجوی مناطق"""
    id = serializers.CharField()
    name = serializers.CharField()
    parent_region_id = serializers.CharField(allow_null=True)
    parent_region_name = serializers.CharField(allow_null=True)


# =====================================================
# Favorite & Review Serializers
# =====================================================

class FavoriteSerializer(serializers.ModelSerializer):
    """سریالایزر برای علاقه‌مندی‌ها"""
    facility_detail = FacilityListSerializer(source='facility', read_only=True)
    # Don't access user object directly - it's in a different database
    # Just return user_id as integer
    user_id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Favorite
        fields = [
            'favorite_id', 'user_id',
            'facility', 'facility_detail',
            'created_at'
        ]
        read_only_fields = ['favorite_id', 'user_id', 'created_at']
    
    def create(self, validated_data):
        # کاربر از request گرفته می‌شود
        user = self.context['request'].user
        facility = validated_data.get('facility')
        
        # بررسی وجود قبلی
        favorite, created = Favorite.objects.get_or_create(
            user_id=user.pk,
            facility=facility
        )
        
        if not created:
            raise serializers.ValidationError({
                'detail': 'این مکان قبلاً به علاقه‌مندی‌های شما اضافه شده است.'
            })
        
        return favorite


class ReviewSerializer(serializers.ModelSerializer):
    """سریالایزر برای نظرات"""
    # Don't access user object directly - it's in a different database
    user_id = serializers.IntegerField(read_only=True)
    user_name = serializers.SerializerMethodField()
    facility_name = serializers.CharField(source='facility.name_fa', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'user_id', 'user_name',
            'facility', 'facility_name',
            'rating', 'comment',
            'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['review_id', 'user_id', 'is_approved', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        # Return user_id as string since we can't access user object from different DB
        return f"User {obj.user_id}"
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('امتیاز باید بین 1 تا 5 باشد.')
        return value
    
    def create(self, validated_data):
        # کاربر از request گرفته می‌شود
        user = self.context['request'].user
        facility = validated_data.get('facility')
        
        # بررسی وجود نظر قبلی
        if Review.objects.filter(user=user, facility=facility).exists():
            raise serializers.ValidationError({
                'detail': 'شما قبلاً برای این مکان نظر ثبت کرده‌اید. می‌توانید نظر خود را ویرایش کنید.'
            })
        
        validated_data['user'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # فقط کاربر صاحب نظر می‌تواند آن را ویرایش کند
        if instance.user != self.context['request'].user:
            raise serializers.ValidationError({
                'detail': 'شما مجاز به ویرایش این نظر نیستید.'
            })
        
        return super().update(instance, validated_data)


class ReviewCreateSerializer(serializers.ModelSerializer):
    """سریالایزر برای ایجاد نظر جدید"""
    class Meta:
        model = Review
        fields = ['facility', 'rating', 'comment']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('امتیاز باید بین 1 تا 5 باشد.')
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        facility = validated_data.get('facility')
        
        # بررسی وجود نظر قبلی
        if Review.objects.filter(user=user, facility=facility).exists():
            raise serializers.ValidationError({
                'detail': 'شما قبلاً برای این مکان نظر ثبت کرده‌اید.'
            })
        
        validated_data['user'] = user
        return Review.objects.create(**validated_data)


class FacilityFilterSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    village = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    province = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(required=False, allow_blank=True)
    amenity = serializers.CharField(required=False, allow_blank=True)
    price_tier = serializers.CharField(required=False, allow_blank=True)


class RoutingRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['car', 'motorcycle'], default='car')
    origin = serializers.CharField()
    destination = serializers.CharField()
    # waypoints = serializers.CharField(required=False, allow_blank=True)
    avoidTrafficZone = serializers.BooleanField(default=False)
    avoidOddEvenZone = serializers.BooleanField(default=False)
    alternative = serializers.BooleanField(default=False)

    def validate_point(self, value):
        try:
            # Expected input: "lat,lng"
            coords = value.split(',')
            return Point(longitude=coords[1], latitude=coords[0])
        except Exception:
            raise serializers.ValidationError("فرمت مختصات نامعتبر است. لطفا از فرمت 'lat,lng' استفاده کنید.")

    def validate_origin(self, value):
        return self.validate_point(value)

    def validate_destination(self, value):
        return self.validate_point(value)