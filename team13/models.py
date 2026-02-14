# مدل‌های سرویس Facilities & Transportation — مطابق P5_Axiom
# توجه: کاربر (User) در core و دیتابیس default است؛ در اینجا فقط user_id ذخیره می‌شود.

import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# برای سازگاری با SQLite پیش‌فرض، از دو فیلد عرض/طول استفاده شده است.
# در صورت استفاده از PostgreSQL/PostGIS می‌توان از PointField استفاده کرد.


class Place(models.Model):
    """مکان (POI): رستوران، بیمارستان، موزه، هتل، تفریحی."""

    class PlaceType(models.TextChoices):
        ENTERTAINMENT = "entertainment", "تفریحی"
        FOOD = "food", "غذا"
        HOSPITAL = "hospital", "بیمارستان"
        MUSEUM = "museum", "موزه"
        HOTEL = "hotel", "هتل"
        FIRE_STATION = "fire_station", "آتش‌نشانی"
        PHARMACY = "pharmacy", "داروخانه"
        CLINIC = "clinic", "کلینیک"

    place_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_column="place_id"
    )
    type = models.CharField(max_length=32, choices=PlaceType.choices)
    city = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        app_label = "team13"
        db_table = "team13_places"

    def __str__(self):
        return f"{self.get_type_display()} — {self.city or 'بدون شهر'}"


class PlaceTranslation(models.Model):
    """ترجمه نام و توضیح مکان (چندزبانگی)."""

    place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name="translations", db_column="place_id"
    )
    lang = models.CharField(max_length=2, choices=[("fa", "فارسی"), ("en", "English")])
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        app_label = "team13"
        db_table = "team13_place_translations"
        unique_together = [("place", "lang")]

    def __str__(self):
        return f"{self.place_id} ({self.lang})"


class Event(models.Model):
    """رویداد: تاریخ و مکان رویداد."""

    event_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_column="event_id"
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    city = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        app_label = "team13"
        db_table = "team13_events"

    def __str__(self):
        return f"Event {self.event_id} — {self.city or 'بدون شهر'}"


class EventTranslation(models.Model):
    """ترجمه عنوان و توضیح رویداد."""

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="translations", db_column="event_id"
    )
    lang = models.CharField(max_length=2, choices=[("fa", "فارسی"), ("en", "English")])
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        app_label = "team13"
        db_table = "team13_event_translations"
        unique_together = [("event", "lang")]

    def __str__(self):
        return f"{self.event_id} ({self.lang})"


class Image(models.Model):
    """تصویر مرتبط با یک مکان، رویداد، یا مکان در انتظار تأیید (pending_place)."""

    class TargetType(models.TextChoices):
        PLACE = "place", "مکان"
        EVENT = "event", "رویداد"
        PENDING_PLACE = "pending_place", "مکان در انتظار تأیید"

    image_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_column="image_id"
    )
    target_type = models.CharField(max_length=16, choices=TargetType.choices)
    target_id = models.UUIDField()
    image_url = models.URLField(max_length=500)
    is_approved = models.BooleanField(default=False, db_column="is_approved")

    class Meta:
        app_label = "team13"
        db_table = "team13_images"

    def __str__(self):
        return f"{self.target_type}:{self.target_id}"


class Comment(models.Model):
    """نظر/امتیاز برای یک مکان یا رویداد."""

    class TargetType(models.TextChoices):
        PLACE = "place", "مکان"
        EVENT = "event", "رویداد"

    comment_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_column="comment_id"
    )
    target_type = models.CharField(max_length=16, choices=TargetType.choices)
    target_id = models.UUIDField()
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    body = models.TextField(blank=True)  # متن نظر (کامنت)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True, db_column="is_approved")  # امتیاز بدون متن فوراً نمایش؛ نظر متنی پس از تأیید ادمین

    class Meta:
        app_label = "team13"
        db_table = "team13_comments"

    def __str__(self):
        return f"{self.target_type}:{self.target_id} — {self.rating}"


class HotelDetails(models.Model):
    """جزئیات هتل (یک به یک با Place)."""

    place = models.OneToOneField(
        Place, on_delete=models.CASCADE, primary_key=True, related_name="hotel_details", db_column="place_id"
    )
    stars = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    price_range = models.CharField(max_length=64, blank=True)  # مثلاً حداکثر قیمت به تومان

    class Meta:
        app_label = "team13"
        db_table = "team13_hotel_details"

    def __str__(self):
        return f"Hotel {self.place_id} — {self.stars}*"


class RestaurantDetails(models.Model):
    """جزئیات رستوران."""

    place = models.OneToOneField(
        Place, on_delete=models.CASCADE, primary_key=True, related_name="restaurant_details", db_column="place_id"
    )
    cuisine = models.CharField(max_length=128, blank=True)
    avg_price = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        app_label = "team13"
        db_table = "team13_restaurant_details"

    def __str__(self):
        return f"Restaurant {self.place_id} — {self.cuisine}"


class MuseumDetails(models.Model):
    """جزئیات موزه."""

    place = models.OneToOneField(
        Place, on_delete=models.CASCADE, primary_key=True, related_name="museum_details", db_column="place_id"
    )
    open_at = models.TimeField(null=True, blank=True)
    close_at = models.TimeField(null=True, blank=True)
    ticket_price = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        app_label = "team13"
        db_table = "team13_museum_details"

    def __str__(self):
        return f"Museum {self.place_id}"


class PlaceAmenity(models.Model):
    """امکانات یک مکان (پارکینگ، استخر، وای‌فای و ...)."""

    place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name="amenities", db_column="place_id"
    )
    amenity_name = models.CharField(max_length=128)

    class Meta:
        app_label = "team13"
        db_table = "team13_place_amenities"
        unique_together = [("place", "amenity_name")]

    def __str__(self):
        return f"{self.place_id} — {self.amenity_name}"


class RouteLog(models.Model):
    """ثبت سفر/مسیر کاربر (مبدأ، مقصد، نوع حمل‌ونقل)."""

    class TravelMode(models.TextChoices):
        CAR = "car", "خودرو"
        WALK = "walk", "پیاده"
        TRANSIT = "transit", "حمل‌ونقل عمومی"

    # user در core و در دیتابیس دیگر است؛ فقط شناسه ذخیره می‌شود
    user_id = models.UUIDField(null=True, blank=True, db_index=True)
    source_place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name="routes_from", db_column="source_place_id"
    )
    destination_place = models.ForeignKey(
        Place, on_delete=models.CASCADE, related_name="routes_to", db_column="destination_place_id"
    )
    travel_mode = models.CharField(max_length=16, choices=TravelMode.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "team13"
        db_table = "team13_route_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source_place_id} → {self.destination_place_id} ({self.travel_mode})"


class RouteContribution(models.Model):
    """پیشنهاد مسیر توسط کاربر؛ پس از تأیید ادمین، دو مکان و یک RouteLog ساخته می‌شود."""

    class TravelMode(models.TextChoices):
        CAR = "car", "خودرو"
        WALK = "walk", "پیاده"
        TRANSIT = "transit", "حمل‌ونقل عمومی"

    contribution_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_column="contribution_id"
    )
    source_address = models.TextField(help_text="آدرس مبدأ (از روی عرض/طول ثابت شده)")
    source_latitude = models.FloatField()
    source_longitude = models.FloatField()
    destination_address = models.TextField(help_text="آدرس مقصد (از روی عرض/طول ثابت شده)")
    destination_latitude = models.FloatField()
    destination_longitude = models.FloatField()
    travel_mode = models.CharField(max_length=16, choices=TravelMode.choices, default=TravelMode.CAR)
    user_id = models.UUIDField(null=True, blank=True, db_index=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "team13"
        db_table = "team13_route_contributions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.source_address[:30]} → {self.destination_address[:30]} ({self.get_travel_mode_display()})"


class PlaceContribution(models.Model):
    """پیشنهاد مکان توسط کاربر؛ پس از تأیید به Place تبدیل می‌شود."""

    contribution_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_column="contribution_id"
    )
    name_fa = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=32, choices=Place.PlaceType.choices)
    address = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=255, blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team13_place_contributions",
        db_column="submitted_by_id",
        db_constraint=False,
    )
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "team13"
        db_table = "team13_place_contributions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name_fa} ({self.contribution_id})"


class TeamAdmin(models.Model):
    """کاربران مجاز به عنوان ادمین تیم ۱۳ (شناسه کاربر از دیتابیس default، بدون FK برای جلوگیری از خطای cross-DB)."""

    user_id = models.CharField(max_length=64, unique=True, db_index=True, db_column="user_id", null=True, blank=True)

    class Meta:
        app_label = "team13"
        db_table = "team13_team_admins"

    def __str__(self):
        return str(self.user_id)
