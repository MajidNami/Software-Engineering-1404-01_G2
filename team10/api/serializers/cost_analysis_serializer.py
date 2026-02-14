from rest_framework import serializers


class CostAnalysisSerializer(serializers.Serializer):
    """Serializer for cost analysis response."""

    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    budget_limit = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_within_budget = serializers.BooleanField()
    analysis = serializers.CharField()
    percentage_of_budget = serializers.FloatField()
