from django.db import models
import uuid

class UserProfileFeature(models.Model):
    feature_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=50, db_index=True)
    category = models.CharField(max_length=100)
    weight = models.FloatField(default=0.0)
    source = models.CharField(max_length=20, choices=[('manual', 'Manual'), ('interaction', 'Interaction')])
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profile_features'

class UserInteraction(models.Model):
    interaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=50, null=False, db_index=True)
    item_id = models.CharField(max_length=50, null=False, db_index=True)
    item_type = models.CharField(max_length=20, choices=[('article', 'Article'), ('place', 'Place'), ('event', 'Event'), ('route', 'Route')], null=False)
    interaction_type = models.CharField(max_length=20, choices=[('view', 'View'), ('like', 'Like'), ('rate', 'Rate')], null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_interactions'

class LocationContext(models.Model):
    location_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=50, null=False, db_index=True)
    location = models.CharField(max_length=100, help_text="e.g., POINT(51.3890 35.6892)")
    radius_km = models.FloatField(default=100.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'location_context'

class Recommendation(models.Model):
    recommendation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=50, null=False, db_index=True)
    item_id = models.CharField(max_length=50, null=False, db_index=True)
    item_type = models.CharField(max_length=20, choices=[('article', 'Article'), ('place', 'Place'), ('event', 'Event'), ('route', 'Route')], null=False)
    score = models.FloatField(null=False)
    reason_type = models.CharField(max_length=20, choices=[('interest', 'Interest'), ('location', 'Location'), ('popularity', 'Popularity')], null=False)
    reason_description = models.TextField(blank=True)
    user_feedback = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')], blank=True, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    feedback_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'recommendations'