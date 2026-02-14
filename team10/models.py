from django.db import models
from django.conf import settings
from django.utils import timezone


class TripRequirements(models.Model):
    """Database model for trip requirements."""

    BUDGET_LEVEL_CHOICES = [
        ('ECONOMY', 'Economy'),
        ('MODERATE', 'Moderate'),
        ('LUXURY', 'Luxury'),
    ]

    user_id = models.CharField(max_length=255, db_index=True)  # Hash string from central auth
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    destination_city_id = models.IntegerField(null=True, blank=True)
    destination_name = models.CharField(max_length=200)
    region_id = models.CharField(max_length=255, null=True, blank=True)
    budget_level = models.CharField(max_length=20, choices=BUDGET_LEVEL_CHOICES, default='MODERATE')
    travelers_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'trip_requirements'
        verbose_name_plural = 'Trip Requirements'

    def __str__(self):
        return f"Requirements for user {self.user_id} - {self.destination_name}"


class PreferenceConstraint(models.Model):
    """Database model for preference constraints."""

    requirements = models.ForeignKey(TripRequirements, on_delete=models.CASCADE, related_name='constraints')
    description = models.TextField()
    tag = models.CharField(max_length=100)

    class Meta:
        db_table = 'preference_constraints'

    def __str__(self):
        return f"{self.tag}: {self.description}"


class Trip(models.Model):
    """Database model for trips."""

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('IN_PROGRESS', 'In Progress'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
        ('NEEDS_REGENERATION', 'Needs Regeneration'),
    ]

    user_id = models.CharField(max_length=255, db_index=True)  # Hash string from central auth
    requirements = models.ForeignKey(TripRequirements, on_delete=models.CASCADE, related_name='trips')
    destination_name = models.CharField(max_length=200, default='')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'trips'
        ordering = ['-created_at']

    def __str__(self):
        return f"Trip {self.id} - User {self.user_id} ({self.status})"

    def _get_trip_date_range(self):
        req = getattr(self, "requirements", None)
        if not req:
            return None, None

        start_at = getattr(req, "start_at", None)
        end_at = getattr(req, "end_at", None)
        if not start_at or not end_at:
            return None, None

        return timezone.localdate(start_at), timezone.localdate(end_at)

    @property
    def display_status(self) -> str:
        start_date, end_date = self._get_trip_date_range()
        if not start_date or not end_date:
            return self.status

        today = timezone.localdate()
        if start_date > today:
            return "DRAFT"
        if start_date <= today < end_date:
            return "IN_PROGRESS"
        return "COMPLETED"

    @property
    def display_status_label_fa(self) -> str:
        status_display = {
            "DRAFT": "پیش‌نویس",
            "IN_PROGRESS": "در حال اجرا",
            "COMPLETED": "پایان‌یافته",
        }
        return status_display.get(self.display_status, "نامشخص")

    def calculate_total_cost(self):
        """Calculate total cost of the trip including activities, hotels, and transportation."""
        daily_cost = sum(plan.cost for plan in self.daily_plans.all())
        hotel_cost = sum(schedule.cost for schedule in self.hotel_schedules.all())
        transfer_cost = sum(transfer.cost for transfer in self.transfer_plans.all())
        return daily_cost + hotel_cost + transfer_cost

    def get_cost_breakdown(self):
        """Get detailed cost breakdown by category."""
        daily_cost = sum(plan.cost for plan in self.daily_plans.all())
        hotel_cost = sum(schedule.cost for schedule in self.hotel_schedules.all())
        transfer_cost = sum(transfer.cost for transfer in self.transfer_plans.all())
        
        return {
            'activities': float(daily_cost),
            'hotels': float(hotel_cost),
            'transportation': float(transfer_cost),
            'total': float(daily_cost + hotel_cost + transfer_cost)
        }


class DailyPlan(models.Model):
    """Database model for daily plans."""

    ACTIVITY_CHOICES = [
        ('SIGHTSEEING', 'Sightseeing'),
        ('FOOD', 'Food'),
        ('SHOPPING', 'Shopping'),
        ('OUTDOOR', 'Outdoor'),
        ('CULTURE', 'Culture'),
        ('RELAX', 'Relax'),
        ('NIGHTLIFE', 'Nightlife'),
        ('TRANSPORT', 'Transport'),
        ('OTHER', 'Other'),
    ]

    SOURCE_CHOICES = [
        ('WIKI', 'Wiki'),
        ('RECOMMENDATION', 'Recommendation'),
        ('FACILITIES', 'Facilities'),
        ('MANUAL', 'Manual'),
        ('EVENT', 'Event'),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='daily_plans')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    facility_id = models.IntegerField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    description = models.TextField()
    place_source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES)

    class Meta:
        db_table = 'daily_plans'
        ordering = ['start_at']

    def __str__(self):
        return f"{self.activity_type} - {self.description[:50]}"


class HotelSchedule(models.Model):
    """Database model for hotel schedules."""

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='hotel_schedules')
    hotel_id = models.IntegerField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    rooms_count = models.IntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'hotel_schedules'
        ordering = ['start_at']

    def __str__(self):
        return f"Hotel {self.hotel_id} - {self.start_at.date()} to {self.end_at.date()}"


class TransferPlan(models.Model):
    """Database model for transfers between activities."""

    TRANSPORT_MODE_CHOICES = [
        ('WALKING', 'پیاده‌روی'),
        ('DRIVING', 'خودرو شخصی'),
        ('PUBLIC_TRANSIT', 'حمل‌ونقل عمومی'),
        ('TAXI', 'تاکسی'),
    ]

    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='transfer_plans')
    from_daily_plan = models.ForeignKey(DailyPlan, on_delete=models.CASCADE, related_name='transfers_from', null=True, blank=True)
    to_daily_plan = models.ForeignKey(DailyPlan, on_delete=models.CASCADE, related_name='transfers_to', null=True, blank=True)
    from_facility_id = models.IntegerField()
    to_facility_id = models.IntegerField()
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    duration_minutes = models.IntegerField(default=0)
    transport_mode = models.CharField(max_length=20, choices=TRANSPORT_MODE_CHOICES, default='WALKING')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transfer_time = models.DateTimeField()  # When this transfer happens

    class Meta:
        db_table = 'transfer_plans'
        ordering = ['transfer_time']

    def __str__(self):
        return f"Transfer: {self.transport_mode} - {self.distance_km}km"
    
    def get_transport_mode_display_fa(self):
        """Get Persian display for transport mode."""
        mode_display = {
            'WALKING': 'پیاده‌روی',
            'DRIVING': 'خودرو شخصی',
            'PUBLIC_TRANSIT': 'حمل‌ونقل عمومی',
            'TAXI': 'تاکسی',
        }
        return mode_display.get(self.transport_mode, self.transport_mode)
