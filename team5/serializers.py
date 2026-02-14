from rest_framework import serializers
from .models import Place, RecommendationLog

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['place_id', 'name', 'total_score', 'feature']

class RecommendationResponseSerializer(serializers.Serializer):
    place_id = serializers.CharField()
    name = serializers.CharField()
    score = serializers.FloatField()
    reason = serializers.CharField()