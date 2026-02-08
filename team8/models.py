import uuid
from django.db import models
from django.conf import settings


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        db_table = "categories"

    def __str__(self):
        return self.name


class Place(models.Model):
    id = models.BigAutoField(primary_key=True)

    title = models.CharField(max_length=150)
    description = models.TextField()

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="places"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "places"

    def __str__(self):
        return self.title


class Media(models.Model):

    class ContentStatus(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="media"
    )

    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="media"
    )

    s3_object_key = models.CharField(max_length=255)
    bucket_name = models.CharField(max_length=50)
    mime_type = models.CharField(max_length=50)

    caption = models.TextField(blank=True)
    is_edited = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=ContentStatus.choices,
        default=ContentStatus.PENDING
    )

    ai_confidence = models.FloatField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "media"


class Rating(models.Model):
    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    score = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ratings"
        unique_together = ("user", "place")


class Comment(models.Model):

    class ContentStatus(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    media = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comments"
    )

    content = models.TextField()
    is_edited = models.BooleanField(default=False)

    status = models.CharField(
        max_length=20,
        choices=ContentStatus.choices,
        default=ContentStatus.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "comments"


class Report(models.Model):

    class ReportTarget(models.TextChoices):
        MEDIA = "media"
        COMMENT = "comment"

    class ReportStatus(models.TextChoices):
        OPEN = "open"
        REVIEWED = "reviewed"
        RESOLVED = "resolved"

    id = models.BigAutoField(primary_key=True)

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports"
    )

    target_type = models.CharField(
        max_length=20,
        choices=ReportTarget.choices
    )

    reported_media = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports"
    )

    reported_comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reports"
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


class Notification(models.Model):
    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"


class ActivityLog(models.Model):
    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_logs"
    )

    action_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=50)

    metadata = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity_logs"
