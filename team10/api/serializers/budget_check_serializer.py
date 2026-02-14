from rest_framework import serializers


class BudgetCheckSerializer(serializers.Serializer):
    """Serializer for budget check request."""

    budget_limit = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default="USD")
