import uuid
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Avg


class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.username


class Province(models.Model):
    province_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "provinces"

    def __str__(self):
        return self.name


class City(models.Model):
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
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "categories"

    def __str__(self):
        return self.name


class Place(models.Model):
    place_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
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
        return self.ratings.aggregate(Avg('score'))['score__avg']

    @property
    def rating_count(self):
        return self.ratings.count()


class Media(models.Model):
    class ContentStatus(models.TextChoices):
        PENDING_AI = "PENDING_AI"
        PENDING_ADMIN = "PENDING_ADMIN"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"

    media_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="media",
        db_column="user_id"
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="media",
        db_column="place_id"
    )
    s3_object_key = models.CharField(max_length=255)
    bucket_name = models.CharField(max_length=50, default='tourism-prod-media')
    mime_type = models.CharField(max_length=50)
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
            models.Index(fields=['user'], name='idx_media_user'),
            models.Index(fields=['place', 'status'], name='idx_media_place_status'),
            models.Index(fields=['deleted_at'], name='idx_media_deleted_at'),
        ]


class Post(models.Model):
    class ContentStatus(models.TextChoices):
        PENDING_AI = "PENDING_AI"
        PENDING_ADMIN = "PENDING_ADMIN"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"

    post_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        db_column="user_id"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        db_column="parent_id"
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="posts",
        db_column="place_id"
    )
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
    # Per-component AI verdicts (for coordinated approval when post has both text+media)
    text_ai_status = models.CharField(
        max_length=20, choices=ContentStatus.choices,
        default=ContentStatus.PENDING_AI
    )
    media_ai_status = models.CharField(
        max_length=20, choices=ContentStatus.choices,
        null=True, blank=True  # NULL when post has no media attachment
    )
    ai_confidence = models.FloatField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "posts"
        indexes = [
            models.Index(fields=['user'], name='idx_posts_user'),
            models.Index(fields=['place', 'status'], name='idx_posts_place_status'),
            models.Index(fields=['parent'], name='idx_posts_parent'),
            models.Index(fields=['-created_at'], name='idx_posts_created_desc'),
            models.Index(fields=['media'], name='idx_posts_media'),
            models.Index(fields=['deleted_at'], name='idx_posts_deleted_at'),
        ]

    @property
    def like_count(self):
        return self.votes.filter(is_like=True).count()

    @property
    def dislike_count(self):
        return self.votes.filter(is_like=False).count()

    @property
    def reply_count(self):
        return self.replies.filter(deleted_at__isnull=True).count()


class Rating(models.Model):
    rating_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ratings",
        db_column="user_id"
    )
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
            models.UniqueConstraint(
                fields=['user', 'place'],
                name='unique_user_place_rating'
            ),
            models.CheckConstraint(
                check=models.Q(score__gte=1) & models.Q(score__lte=5),
                name='valid_rating_score'
            )
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_ratings_user'),
            models.Index(fields=['place'], name='idx_ratings_place'),
        ]


class PostVote(models.Model):
    vote_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_votes",
        db_column="user_id"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="votes",
        db_column="post_id"
    )
    is_like = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_votes"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_user_post_vote'
            )
        ]
        indexes = [
            models.Index(fields=['user'], name='idx_post_votes_user'),
            models.Index(fields=['post'], name='idx_post_votes_post'),
            models.Index(fields=['post', 'is_like'], name='idx_post_votes_post_like'),
        ]


class ActivityLog(models.Model):
    log_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
        db_column="user_id"
    )
    action_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=50, null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity_logs"
        indexes = [
            models.Index(fields=['user'], name='idx_activity_logs_user'),
            models.Index(fields=['action_type'], name='idx_activity_logs_action'),
            models.Index(fields=['created_at'], name='idx_activity_logs_created'),
        ]


class Notification(models.Model):
    notification_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_column="user_id"
    )
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        indexes = [
            models.Index(fields=['user'], name='idx_notifications_user'),
            models.Index(fields=['is_read'], name='idx_notifications_read'),
        ]


class Report(models.Model):
    class ReportStatus(models.TextChoices):
        OPEN = "OPEN"
        RESOLVED = "RESOLVED"
        DISMISSED = "DISMISSED"

    class ReportTarget(models.TextChoices):
        MEDIA = "MEDIA"
        POST = "POST"

    report_id = models.BigAutoField(primary_key=True)
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports",
        db_column="reporter_id"
    )
    target_type = models.CharField(max_length=10, choices=ReportTarget.choices)
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
        max_length=10,
        choices=ReportStatus.choices,
        default=ReportStatus.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reports"
        indexes = [
            models.Index(fields=['reporter'], name='idx_reports_reporter'),
            models.Index(fields=['status'], name='idx_reports_status'),
        ]
