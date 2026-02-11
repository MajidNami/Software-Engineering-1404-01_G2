from rest_framework import serializers


class StyleUpdateSerializer(serializers.Serializer):
    """Serializer for style update request."""

    styles = serializers.ListField(
        child=serializers.CharField(max_length=100)
    )
