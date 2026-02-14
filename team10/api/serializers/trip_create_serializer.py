from rest_framework import serializers


class PreferenceConstraintSerializer(serializers.Serializer):
    """Serializer for preference constraint."""

    description = serializers.CharField()
    tag = serializers.CharField(max_length=100)


class TripCreateSerializer(serializers.Serializer):
    """Serializer for trip creation request."""

    user_id = serializers.IntegerField()
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    destination_city_id = serializers.IntegerField()
    constraints = PreferenceConstraintSerializer(many=True, required=False)
    budget_limit = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
