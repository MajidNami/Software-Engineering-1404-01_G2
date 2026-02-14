from rest_framework import serializers
from data.models import (
    Trip, TripDay, TripItem, ItemDependency,
    ShareLink, Vote, TripReview, UserMedia
)


class CamelCaseFieldMixin:
    """Mixin to handle camelCase field names in input"""

    def to_internal_value(self, data):
        """Convert camelCase to snake_case"""
        camel_to_snake = {
            'startDate': 'start_date',
            'endDate': 'end_date',
            'budgetLevel': 'budget_level',
        }
        converted_data = {}
        for key, value in data.items():
            converted_key = camel_to_snake.get(key, key)
            converted_data[converted_key] = value
        return super().to_internal_value(converted_data)


class TripItemSerializer(serializers.ModelSerializer):
    """Serializer for TripItem model with custom field names"""

    id = serializers.IntegerField(source='item_id', read_only=True)
    type = serializers.CharField(source='item_type')
    summery = serializers.CharField(
        source='wiki_summary', allow_blank=True, required=False)
    cost = serializers.SerializerMethodField()
    address = serializers.CharField(
        source='address_summary', allow_blank=True, required=False)
    url = serializers.URLField(
        source='wiki_link', allow_blank=True, required=False)

    class Meta:
        model = TripItem
        fields = [
            'id', 'category', 'type', 'title', 'start_time', 'end_time',
            'summery', 'cost', 'address', 'url'
        ]
        read_only_fields = ['id']

    def get_cost(self, obj):
        """Convert decimal to float for cost"""
        return float(obj.estimated_cost) if obj.estimated_cost else 0

    def validate(self, data):
        """Validate time fields"""
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    "End time must be after start time"
                )

        return data


class TripItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating TripItem (accepts all fields)"""

    class Meta:
        model = TripItem
        fields = [
            'item_type', 'place_ref_id', 'title', 'category',
            'address_summary', 'lat', 'lng', 'wiki_summary', 'wiki_link',
            'main_image_url', 'start_time', 'end_time', 'duration_minutes',
            'sort_order', 'is_locked', 'price_tier', 'estimated_cost'
        ]

    def validate(self, data):
        """Validate time fields"""
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    "End time must be after start time"
                )

        if 'duration_minutes' in data and data['duration_minutes'] < 60:
            raise serializers.ValidationError(
                "Duration must be at least 60 minutes"
            )

        return data


class ItemDependencySerializer(serializers.ModelSerializer):
    """Serializer for ItemDependency model"""

    prerequisite_title = serializers.CharField(
        source='prerequisite_item.title',
        read_only=True
    )

    class Meta:
        model = ItemDependency
        fields = [
            'dependency_id', 'item', 'prerequisite_item',
            'prerequisite_title', 'dependency_type', 'violation_action'
        ]
        read_only_fields = ['dependency_id']


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for Vote model"""

    class Meta:
        model = Vote
        fields = ['vote_id', 'item', 'guest_session_id',
                  'is_upvote', 'created_at']
        read_only_fields = ['vote_id', 'created_at']


class TripDaySerializer(serializers.ModelSerializer):
    """Serializer for TripDay model with custom field names"""

    day_number = serializers.IntegerField(source='day_index', read_only=True)
    date = serializers.DateField(source='specific_date', read_only=True)
    items = TripItemSerializer(many=True, read_only=True)

    class Meta:
        model = TripDay
        fields = ['day_number', 'date', 'items']
        read_only_fields = ['day_number', 'date']


class ShareLinkSerializer(serializers.ModelSerializer):
    """Serializer for ShareLink model"""

    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = ShareLink
        fields = [
            'link_id', 'token', 'expires_at', 'permission',
            'created_at', 'is_expired'
        ]
        read_only_fields = ['link_id', 'token', 'created_at']

    def get_is_expired(self, obj):
        """Check if link is expired"""
        from django.utils import timezone
        return obj.expires_at < timezone.now()


class TripReviewSerializer(serializers.ModelSerializer):
    """Serializer for TripReview model"""

    class Meta:
        model = TripReview
        fields = [
            'review_id', 'trip', 'item', 'rating',
            'comment', 'sent_to_central_service', 'created_at'
        ]
        read_only_fields = ['review_id',
                            'created_at', 'sent_to_central_service']

    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class UserMediaSerializer(serializers.ModelSerializer):
    """Serializer for UserMedia model"""

    class Meta:
        model = UserMedia
        fields = [
            'media_id', 'trip', 'user_id',
            'media_url', 'caption', 'media_type', 'uploaded_at'
        ]
        read_only_fields = ['media_id', 'uploaded_at']


class TripListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for trip lists"""

    id = serializers.IntegerField(source='trip_id', read_only=True)
    total_cost = serializers.DecimalField(source='total_estimated_cost', max_digits=12, decimal_places=2, read_only=True)
    days_count = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = [
            'id', 'trip_id', 'title', 'location', 'province', 'city',
            'start_date', 'end_date', 'duration_days',
            'budget_level', 'travel_style', 'status',
            'days_count', 'total_cost', 'created_at'
        ]
        read_only_fields = ['id', 'trip_id', 'created_at', 'end_date', 'total_cost']

    def get_days_count(self, obj):
        """Get number of days in trip"""
        return obj.days.count() if hasattr(obj, 'days') else 0

    def get_location(self, obj):
        """Get formatted location"""
        return obj.city if obj.city else obj.province


class TripDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single trip view with custom field names"""

    id = serializers.IntegerField(source='trip_id', read_only=True)
    total_cost = serializers.SerializerMethodField()
    style = serializers.CharField(source='travel_style', read_only=True)
    days = TripDaySerializer(many=True, read_only=True)

    class Meta:
        model = Trip
        fields = [
            'id', 'title', 'province', 'city', 'start_date', 'end_date',
            'duration_days', 'style', 'budget_level', 'status',
            'total_cost', 'days', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'end_date', 'total_cost']

    def get_total_cost(self, obj):
        """Convert decimal to float for total_cost"""
        return float(obj.total_estimated_cost)


class TripCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating trips with camelCase support"""

    style = serializers.CharField(source='travel_style', required=False, allow_null=True)
    startDate = serializers.DateField(source='start_date', required=True)
    endDate = serializers.DateField(source='end_date', required=False)
    budget_level = serializers.CharField(required=False, allow_null=True)
    density = serializers.CharField(required=False, allow_null=True)
    interests = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Trip
        fields = [
            'province', 'city', 'startDate', 'endDate', 'style',
            'density', 'interests', 'budget_level'
        ]

    def create(self, validated_data):
        """Create trip with default values"""
        # Calculate duration_days from start_date and end_date
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')

        if end_date is None and start_date is not None:
            # Default to 3 days if end_date not provided
            # duration = (end - start).days + 1, so for 3 days: end = start + 2
            from datetime import timedelta
            end_date = start_date + timedelta(days=2)
            validated_data['end_date'] = end_date

        if start_date and end_date:
            duration_days = (end_date - start_date).days + 1
            validated_data['duration_days'] = duration_days
        else:
            validated_data['duration_days'] = 3  # Default duration

        # Set default values for required fields if None
        if validated_data.get('travel_style') is None:
            validated_data['travel_style'] = 'SOLO'
        if validated_data.get('budget_level') is None:
            validated_data['budget_level'] = 'MEDIUM'

        # Set default values
        validated_data.setdefault('daily_available_hours', 8)
        validated_data.setdefault('generation_strategy', 'MIXED')
        validated_data.setdefault('status', 'ACTIVE')

        # Generate title
        city = validated_data.get('city')
        province = validated_data.get('province')
        location = city if city else province
        validated_data['title'] = f'Trip to {location}'

        return super().create(validated_data)
