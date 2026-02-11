from rest_framework import serializers


class DailyPlanSerializer(serializers.Serializer):
    """Serializer for daily plan."""

    id = serializers.IntegerField(required=False)
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    facility_id = serializers.IntegerField()
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    activity_type = serializers.CharField(max_length=50)
    description = serializers.CharField()
    place_source_type = serializers.CharField(max_length=50)


class HotelScheduleSerializer(serializers.Serializer):
    """Serializer for hotel schedule."""

    id = serializers.IntegerField(required=False)
    hotel_id = serializers.IntegerField()
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    rooms_count = serializers.IntegerField()
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)


class TripSerializer(serializers.Serializer):
    """Serializer for trip."""

    id = serializers.IntegerField(required=False)
    user_id = serializers.IntegerField()
    requirements_id = serializers.IntegerField()
    status = serializers.CharField(max_length=50)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    daily_plans = DailyPlanSerializer(many=True)
    hotel_schedules = HotelScheduleSerializer(many=True)
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
