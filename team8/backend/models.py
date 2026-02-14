import uuid
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Avg, Count


class Province(models.Model):
    """Iranian provinces (استان) - for user selection/filtering"""
    province_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "provinces"

    def __str__(self):
        return self.name


class City(models.Model):
    """Cities within provinces - for user selection/filtering"""
    city_id = models.AutoField(primary_key=True)
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="cities",
        db_column="province_id"
    )
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "cities"
        constraints = [
            models.UniqueConstraint(
                fields=['province', 'name'],
                name='unique_city_per_province'
            )
        ]
        indexes = [
            models.Index(fields=['province'], name='idx_cities_province'),
        ]

    def __str__(self):
        return f"{self.name}, {self.province.name}"


class Category(models.Model):
    """Place categories - for user selection/filtering"""
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "categories"

    def __str__(self):
        return self.name


class Place(models.Model):
    """
    Places that users can comment on.
    Minimal info - just enough for selection and search.
    """
    place_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    
    # Location (for categorization and search)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="places",
        db_column="city_id"
    )
    location = gis_models.PointField(geography=True, srid=4326, null=True, blank=True)
    
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="places",
        db_column="category_id"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "places"
        indexes = [
            models.Index(fields=['city'], name='idx_places_city'),
            models.Index(fields=['category'], name='idx_places_category'),
        ]

    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        """Calculate average rating (1-5 stars)"""
        return self.ratings.aggregate(Avg('score'))['score__avg']
    
    @property
    def rating_count(self):
        """Total number of ratings"""
        return self.ratings.count()


class Media(models.Model):
    """
    Media files (images/videos) without captions.
    Caption text belongs to the Post that references this media.
    """
    class ContentStatus(models.TextChoices):
        PENDING_AI = "PENDING_AI"
        PENDING_ADMIN = "PENDING_ADMIN"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"

    media_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User reference (denormalized - frozen at creation)
    user_id = models.UUIDField(db_index=True)
    user_name = models.CharField(max_length=150)
    
    place = models.ForeignKey(
        Place, 
        on_delete=models.CASCADE, 
        related_name="media",
        db_column="place_id"
    )
    
    # S3 Storage
    s3_object_key = models.CharField(max_length=255)
    bucket_name = models.CharField(max_length=50, default='tourism-prod-media')
    mime_type = models.CharField(max_length=50)
    
    # Moderation
    status = models.CharField(
        max_length=20,
        choices=ContentStatus.choices,
        default=ContentStatus.PENDING_AI
    )
    ai_confidence = models.FloatField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "media"
        indexes = [
            models.Index(fields=['user_id'], name='idx_media_user'),
            models.Index(fields=['place', 'status'], name='idx_media_place_status'),
        ]


class Post(models.Model):
    """
    Posts (formerly comments) contain text content.
    Can optionally attach media. The post's content serves as the media's caption.
    """
    class ContentStatus(models.TextChoices):
        PENDING_AI = "PENDING_AI"
        PENDING_ADMIN = "PENDING_ADMIN"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"

    post_id = models.BigAutoField(primary_key=True)
    
    # User reference (denormalized - frozen at creation)
    user_id = models.UUIDField(db_index=True)
    user_name = models.CharField(max_length=150)
    
    # Threading (for replies)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        db_column="parent_id"
    )
    
    # Target place (required)
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="posts",
        db_column="place_id"
    )
    
    # Optional media attachment
    media = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        db_column="media_id"
    )
    
    content = models.TextField()
    is_edited = models.BooleanField(default=False)
    
    status = models.CharField(
        max_length=20,
        choices=ContentStatus.choices,
        default=ContentStatus.PENDING_AI
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "posts"
        indexes = [
            models.Index(fields=['user_id'], name='idx_posts_user'),
            models.Index(fields=['place', 'status'], name='idx_posts_place_status'),
            models.Index(fields=['parent'], name='idx_posts_parent'),
            models.Index(fields=['-created_at'], name='idx_posts_created_desc'),  # For feed sorting
        ]
    
    @property
    def like_count(self):
        """Count of likes"""
        return self.votes.filter(is_like=True).count()
    
    @property
    def dislike_count(self):
        """Count of dislikes"""
        return self.votes.filter(is_like=False).count()
    
    @property
    def reply_count(self):
        """Count of direct replies"""
        return self.replies.filter(deleted_at__isnull=True).count()


class Rating(models.Model):
    rating_id = models.BigAutoField(primary_key=True)
    
    # User reference (denormalized - frozen at creation)
    user_id = models.UUIDField(db_index=True)
    user_name = models.CharField(max_length=150)
    
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="ratings",
        db_column="place_id"
    )
    
    score = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ratings"
        constraints = [
            models.CheckConstraint(
                check=models.Q(score__gte=1) & models.Q(score__lte=5),
                name='ratings_score_check'
            ),
            models.UniqueConstraint(
                fields=['user_id', 'place'],
                name='unique_user_place_rating'
            )
        ]
        indexes = [
            models.Index(fields=['user_id'], name='idx_ratings_user'),
            models.Index(fields=['place'], name='idx_ratings_place'),
        ]


class PostVote(models.Model):
    """
    Like/Dislike votes on posts.
    Users cannot vote on their own posts (enforced in view logic).
    """
    vote_id = models.BigAutoField(primary_key=True)
    user_id = models.UUIDField(db_index=True)
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="votes",
        db_column="post_id"
    )
    
    is_like = models.BooleanField()  # True = like, False = dislike
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_votes"
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'post'],
                name='unique_user_post_vote'
            )
        ]
        indexes = [
            models.Index(fields=['user_id'], name='idx_post_votes_user'),
            models.Index(fields=['post'], name='idx_post_votes_post'),
            models.Index(fields=['post', 'is_like'], name='idx_post_votes_post_like'),
        ]

    def __str__(self):
        vote_type = "👍" if self.is_like else "👎"
        return f"{vote_type} on Post {self.post_id}"


class ActivityLog(models.Model):
    """Activity logging with validated action types"""
    
    class ActionType(models.TextChoices):
        POST_CREATED = 'POST_CREATED'
        POST_UPDATED = 'POST_UPDATED'
        POST_DELETED = 'POST_DELETED'
        MEDIA_UPLOADED = 'MEDIA_UPLOADED'
        MEDIA_DELETED = 'MEDIA_DELETED'
        RATING_CREATED = 'RATING_CREATED'
        RATING_UPDATED = 'RATING_UPDATED'
        VOTE_CREATED = 'VOTE_CREATED'
        VOTE_UPDATED = 'VOTE_UPDATED'
        REPORT_CREATED = 'REPORT_CREATED'
        REPORT_RESOLVED = 'REPORT_RESOLVED'
        PLACE_CREATED = 'PLACE_CREATED'
        PLACE_UPDATED = 'PLACE_UPDATED'
        USER_LOGIN = 'USER_LOGIN'
        USER_LOGOUT = 'USER_LOGOUT'
    
    log_id = models.BigAutoField(primary_key=True)
    user_id = models.UUIDField(null=True, blank=True, db_index=True)
    action_type = models.CharField(max_length=50, choices=ActionType.choices)
    target_id = models.CharField(max_length=50, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity_logs"
        indexes = [
            models.Index(fields=['user_id'], name='idx_activity_logs_user'),
            models.Index(fields=['action_type'], name='idx_activity_logs_action'),
            models.Index(fields=['created_at'], name='idx_activity_logs_created'),
        ]


class Notification(models.Model):
    notification_id = models.BigAutoField(primary_key=True)
    user_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        indexes = [
            models.Index(fields=['user_id'], name='idx_notifications_user'),
            models.Index(fields=['is_read'], name='idx_notifications_read'),
        ]


class Report(models.Model):
    class ReportTarget(models.TextChoices):
        MEDIA = "MEDIA"
        POST = "POST"
    
    class ReportStatus(models.TextChoices):
        OPEN = "OPEN"
        RESOLVED = "RESOLVED"
        DISMISSED = "DISMISSED"

    report_id = models.BigAutoField(primary_key=True)
    
    # Reporter info (denormalized)
    reporter_id = models.UUIDField(db_index=True)
    reporter_email = models.CharField(max_length=100)
    
    target_type = models.CharField(
        max_length=20,
        choices=ReportTarget.choices
    )
    
    # Polymorphic Target
    reported_media = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
        db_column="reported_media_id"
    )
    reported_post = models.ForeignKey(
        Post,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports",
        db_column="reported_post_id"
    )
    
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reports"
        indexes = [
            models.Index(fields=['reporter_id'], name='idx_reports_reporter'),
            models.Index(fields=['status'], name='idx_reports_status'),
        ]
