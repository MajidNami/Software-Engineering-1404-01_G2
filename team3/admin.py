from django.contrib import admin

from .models import (
    UserProfileFeature,
    UserInteraction,
    LocationContext,
    Recommendation,
    Feedback,
)


@admin.register(UserProfileFeature)
class UserProfileFeatureAdmin(admin.ModelAdmin):
    list_display = ("feature_id", "user_id", "category", "weight", "source", "updated_at")
    search_fields = ("feature_id", "user_id", "category")


@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ("interaction_id", "user_id", "item_id", "item_type", "interaction_type", "created_at")
    search_fields = ("interaction_id", "user_id", "item_id")


@admin.register(LocationContext)
class LocationContextAdmin(admin.ModelAdmin):
    list_display = ("location_id", "user_id", "latitude", "longitude", "radius_km", "created_at")
    search_fields = ("location_id", "user_id")


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("recommendation_id", "user_id", "item_id", "item_type", "score", "reason_type", "generated_at")
    search_fields = ("recommendation_id", "user_id", "item_id")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("feedback_id", "user_id", "recommendation_id", "value", "created_at")
    search_fields = ("feedback_id", "user_id", "recommendation_id")

# Register your models here.
