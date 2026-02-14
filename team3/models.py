from django.db import models
from django.utils import timezone


class UserProfileFeature(models.Model):
    SOURCE_MANUAL = "manual"
    SOURCE_INTERACTION = "interaction"
    SOURCE_CHOICES = [
        (SOURCE_MANUAL, "Manual"),
        (SOURCE_INTERACTION, "Interaction"),
    ]

    feature_id = models.CharField(primary_key=True, max_length=64)
    user_id = models.CharField(max_length=64, db_index=True)
    category = models.CharField(max_length=64)
    weight = models.FloatField()
    source = models.CharField(max_length=32, choices=SOURCE_CHOICES)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "user_profile_features"

    def __str__(self):
        return f"{self.user_id}:{self.category} ({self.weight})"


class UserInteraction(models.Model):
    ITEM_ARTICLE = "article"
    ITEM_PLACE = "place"
    ITEM_EVENT = "event"
    ITEM_ROUTE = "route"
    ITEM_CHOICES = [
        (ITEM_ARTICLE, "Article"),
        (ITEM_PLACE, "Place"),
        (ITEM_EVENT, "Event"),
        (ITEM_ROUTE, "Route"),
    ]

    INTERACTION_VIEW = "view"
    INTERACTION_LIKE = "like"
    INTERACTION_RATE = "rate"
    INTERACTION_ADD = "added_to_plan"
    INTERACTION_REJECT = "rejected"
    INTERACTION_SEARCH = "search"
    INTERACTION_CHOICES = [
        (INTERACTION_VIEW, "View"),
        (INTERACTION_LIKE, "Like"),
        (INTERACTION_RATE, "Rate"),
        (INTERACTION_ADD, "AddedToPlan"),
        (INTERACTION_REJECT, "Rejected"),
        (INTERACTION_SEARCH, "Search"),
    ]

    interaction_id = models.CharField(primary_key=True, max_length=64)
    user_id = models.CharField(max_length=64, db_index=True)
    item_id = models.CharField(max_length=64, db_index=True)
    item_type = models.CharField(max_length=16, choices=ITEM_CHOICES)
    interaction_type = models.CharField(max_length=32, choices=INTERACTION_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "user_interactions"


class LocationContext(models.Model):
    location_id = models.CharField(primary_key=True, max_length=64)
    user_id = models.CharField(max_length=64, db_index=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius_km = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "location_context"


class Recommendation(models.Model):
    FEEDBACK_LIKE = "like"
    FEEDBACK_DISLIKE = "dislike"
    FEEDBACK_NONE = "none"
    FEEDBACK_CHOICES = [
        (FEEDBACK_LIKE, "Like"),
        (FEEDBACK_DISLIKE, "Dislike"),
        (FEEDBACK_NONE, "None"),
    ]

    REASON_INTEREST = "interest"
    REASON_LOCATION = "location"
    REASON_POPULARITY = "popularity"
    REASON_CHOICES = [
        (REASON_INTEREST, "Interest"),
        (REASON_LOCATION, "Location"),
        (REASON_POPULARITY, "Popularity"),
    ]

    recommendation_id = models.CharField(primary_key=True, max_length=64)
    user_id = models.CharField(max_length=64, db_index=True)
    item_id = models.CharField(max_length=64, db_index=True)
    item_type = models.CharField(max_length=16)
    score = models.FloatField()
    reason_type = models.CharField(max_length=16, choices=REASON_CHOICES)
    reason_description = models.TextField(blank=True)
    user_feedback = models.CharField(max_length=16, choices=FEEDBACK_CHOICES, default=FEEDBACK_NONE)
    generated_at = models.DateTimeField(default=timezone.now)
    feedback_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "recommendations"


class Feedback(models.Model):
    feedback_id = models.CharField(primary_key=True, max_length=64)
    user_id = models.CharField(max_length=64, db_index=True)
    recommendation_id = models.CharField(max_length=64, db_index=True)
    value = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "recommendation_feedback"
