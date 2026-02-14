from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import timedelta

User = get_user_model()


def validate_15_minute_intervals(value):
    if value.minute % 15 != 0:
        raise ValidationError('زمان باید مضرب 15 دقیقه باشد')


class BudgetLevelChoices(models.TextChoices):
    ECONOMY = 'ECONOMY', 'اقتصادی'
    MEDIUM = 'MEDIUM', 'معمولی'
    LUXURY = 'LUXURY', 'لوکس'
    UNLIMITED = 'UNLIMITED', 'بدون محدودیت'


class TravelStyleChoices(models.TextChoices):
    SOLO = 'SOLO', 'تنها'
    COUPLE = 'COUPLE', 'دونفره'
    FAMILY = 'FAMILY', 'خانوادگی'
    FRIENDS = 'FRIENDS', 'با دوستان'
    BUSINESS = 'BUSINESS', 'کاری'


class DensityChoices(models.TextChoices):
    RELAXED = 'RELAXED', 'آرام'
    BALANCED = 'BALANCED', 'متعادل'
    INTENSIVE = 'INTENSIVE', 'فشرده'


class ItemTypeChoices(models.TextChoices):
    VISIT = 'VISIT', 'بازدید'
    STAY = 'STAY', 'اقامت'


class PlaceCategoryChoices(models.TextChoices):
    HISTORICAL = 'HISTORICAL', 'تاریخی'
    NATURAL = 'NATURAL', 'طبیعی'
    CULTURAL = 'CULTURAL', 'فرهنگی'
    RECREATIONAL = 'RECREATIONAL', 'تفریحی'
    RELIGIOUS = 'RELIGIOUS', 'مذهبی'
    DINING = 'DINING', 'رستوران'


class PriceTierChoices(models.TextChoices):
    FREE = 'FREE', 'رایگان'
    BUDGET = 'BUDGET', 'ارزان'
    MODERATE = 'MODERATE', 'متوسط'
    EXPENSIVE = 'EXPENSIVE', 'گران'
    LUXURY = 'LUXURY', 'لوکس'


class Trip(models.Model):
    GENERATION_STRATEGY_CHOICES = [
        ('HISTORICAL', 'Historical'),
        ('ECONOMIC', 'Economic'),
        ('MIXED', 'Mixed'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('FINALIZED', 'Finalized'),
        ('COMPLETED', 'Completed'),
    ]

    trip_id = models.BigAutoField(primary_key=True)
    trip_id = models.BigAutoField(primary_key=True)
    # Changed from ForeignKey to CharField because Users live in Core DB (UUID)
    user_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        db_index=True
    )
    copied_from_trip = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='copied_from_trip_id'
    )
    title = models.CharField(max_length=200)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    duration_days = models.IntegerField(validators=[MinValueValidator(1)])
    budget_level = models.CharField(
        max_length=15, choices=BudgetLevelChoices.choices)
    daily_available_hours = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(24)]
    )
    travel_style = models.CharField(
        max_length=15, choices=TravelStyleChoices.choices)
    density = models.CharField(
        max_length=15, choices=DensityChoices.choices, null=True, blank=True)
    interests = models.JSONField(null=True, blank=True)
    generation_strategy = models.CharField(
        max_length=15, choices=GENERATION_STRATEGY_CHOICES)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='ACTIVE')
    total_estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    reminder_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.end_date and self.start_date and self.duration_days:
            self.end_date = self.start_date + \
                timedelta(days=self.duration_days - 1)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'sql_trip'
        app_label = 'data'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', '-created_at']),
            models.Index(fields=['province']),
            models.Index(fields=['city']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        location = self.city if self.city else self.province
        return f"{self.title} - {location}"


class TripDay(models.Model):
    day_id = models.BigAutoField(primary_key=True)
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='days',
        db_column='trip_id'
    )
    day_index = models.IntegerField(validators=[MinValueValidator(1)])
    specific_date = models.DateField()
    start_geo_location = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'sql_trip_day'
        app_label = 'data'
        ordering = ['trip', 'day_index']
        unique_together = [['trip', 'day_index']]
        indexes = [
            models.Index(fields=['trip', 'day_index']),
        ]

    def __str__(self):
        return f"Day {self.day_index} of {self.trip.title}"


class TripItem(models.Model):
    TRANSPORT_CHOICES = [
        ('WALK', 'Walking'),
        ('TAXI', 'Taxi'),
        ('BUS', 'Bus'),
        ('METRO', 'Metro'),
        ('CAR', 'Personal Car'),
    ]

    item_id = models.BigAutoField(primary_key=True)
    day = models.ForeignKey(
        TripDay,
        on_delete=models.CASCADE,
        related_name='items',
        db_column='day_id'
    )
    item_type = models.CharField(
        max_length=10,
        choices=ItemTypeChoices.choices,
        default=ItemTypeChoices.VISIT
    )
    place_ref_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=PlaceCategoryChoices.choices,
        blank=True
    )
    address_summary = models.CharField(max_length=500, blank=True)
    lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    lng = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    wiki_summary = models.TextField(blank=True)
    wiki_link = models.URLField(blank=True)
    main_image_url = models.URLField(blank=True)
    start_time = models.TimeField(validators=[validate_15_minute_intervals])
    end_time = models.TimeField(validators=[validate_15_minute_intervals])
    duration_minutes = models.IntegerField(validators=[MinValueValidator(60)])
    sort_order = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    price_tier = models.CharField(
        max_length=15,
        choices=PriceTierChoices.choices,
        default=PriceTierChoices.FREE
    )
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    transport_mode_to_next = models.CharField(
        max_length=10,
        choices=TRANSPORT_CHOICES,
        blank=True
    )
    travel_time_to_next = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    travel_distance_to_next = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    class Meta:
        db_table = 'sql_trip_item'
        app_label = 'data'
        ordering = ['day', 'sort_order']
        indexes = [
            models.Index(fields=['day', 'sort_order']),
            models.Index(fields=['place_ref_id']),
        ]

    def __str__(self):
        return f"{self.place_ref_id} on {self.day}"


class ItemDependency(models.Model):
    DEPENDENCY_TYPE_CHOICES = [
        ('FINISH_TO_START', 'Finish-to-Start'),
    ]

    VIOLATION_ACTION_CHOICES = [
        ('WARN', 'Warning Only'),
        ('BLOCK', 'Block Action'),
    ]

    dependency_id = models.BigAutoField(primary_key=True)
    item = models.ForeignKey(
        TripItem,
        on_delete=models.CASCADE,
        related_name='dependencies',
        db_column='item_id'
    )
    prerequisite_item = models.ForeignKey(
        TripItem,
        on_delete=models.CASCADE,
        related_name='prerequisite_for',
        db_column='prerequisite_item_id'
    )
    dependency_type = models.CharField(
        max_length=20,
        choices=DEPENDENCY_TYPE_CHOICES,
        default='FINISH_TO_START'
    )
    violation_action = models.CharField(
        max_length=10,
        choices=VIOLATION_ACTION_CHOICES,
        default='WARN'
    )

    class Meta:
        db_table = 'sql_item_dependency'
        app_label = 'data'
        unique_together = [['item', 'prerequisite_item']]
        indexes = [
            models.Index(fields=['item']),
            models.Index(fields=['prerequisite_item']),
        ]

    def __str__(self):
        return f"{self.prerequisite_item} -> {self.item}"


class ShareLink(models.Model):
    PERMISSION_CHOICES = [
        ('VIEW', 'View Only'),
        ('EDIT', 'Can Edit'),
    ]

    link_id = models.BigAutoField(primary_key=True)
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='share_links',
        db_column='trip_id'
    )
    token = models.CharField(
        max_length=128,
        unique=True,
        db_index=True
    )
    expires_at = models.DateTimeField()
    permission = models.CharField(
        max_length=10, choices=PERMISSION_CHOICES, default='VIEW')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sql_share_link'
        app_label = 'data'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['trip', 'expires_at']),
        ]

    def __str__(self):
        return f"Share link for {self.trip.title} ({self.permission})"


class Vote(models.Model):
    vote_id = models.BigAutoField(primary_key=True)
    item = models.ForeignKey(
        TripItem,
        on_delete=models.CASCADE,
        related_name='votes',
        db_column='item_id'
    )
    guest_session_id = models.CharField(
        max_length=128,
        db_index=True
    )
    is_upvote = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sql_vote'
        app_label = 'data'
        unique_together = [['item', 'guest_session_id']]
        indexes = [
            models.Index(fields=['item', 'guest_session_id']),
        ]

    def __str__(self):
        vote_type = "👍" if self.is_upvote else "👎"
        return f"{vote_type} on {self.item}"


class TripReview(models.Model):
    review_id = models.BigAutoField(primary_key=True)
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='reviews',
        db_column='trip_id'
    )
    item = models.ForeignKey(
        TripItem,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reviews',
        db_column='item_id'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    sent_to_central_service = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sql_trip_review'
        app_label = 'data'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['trip', '-created_at']),
            models.Index(fields=['item']),
        ]

    def __str__(self):
        return f"{self.rating}⭐ review on {self.trip.title}"


class UserMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('PHOTO', 'Photo'),
        ('VIDEO', 'Video'),
        ('PANORAMA', 'Panorama'),
    ]

    media_id = models.BigAutoField(primary_key=True)
    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        related_name='media',
        db_column='trip_id'
    )
    # Changed from ForeignKey to CharField because Users live in Core DB (UUID)
    user_id = models.CharField(
        max_length=36,
        db_index=True,
        null=True,
        blank=True
    )
    media_url = models.URLField(max_length=500)
    caption = models.CharField(max_length=500, blank=True)
    media_type = models.CharField(
        max_length=10, choices=MEDIA_TYPE_CHOICES, default='PHOTO')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sql_user_media'
        app_label = 'data'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['trip', '-uploaded_at']),
            models.Index(fields=['user_id', '-uploaded_at']),
        ]

    def __str__(self):
        return f"{self.media_type} for {self.trip.title}"
