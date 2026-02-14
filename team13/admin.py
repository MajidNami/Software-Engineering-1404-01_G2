from django.contrib import admin
from .models import (
    Place,
    PlaceTranslation,
    Event,
    EventTranslation,
    Image,
    Comment,
    HotelDetails,
    RestaurantDetails,
    MuseumDetails,
    PlaceAmenity,
    PlaceContribution,
    RouteLog,
    TeamAdmin,
)

# همهٔ مدل‌های team13 در دیتابیس team13 ذخیره می‌شوند؛ ادمین Django باید از همین دیتابیس بخواند.
TEAM13_DB = "team13"


class Team13DbAdminMixin:
    def get_queryset(self, request):
        return super().get_queryset(request).using(TEAM13_DB)


class PlaceTranslationInline(admin.TabularInline):
    model = PlaceTranslation
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).using(TEAM13_DB)


class PlaceAmenityInline(admin.TabularInline):
    model = PlaceAmenity
    extra = 0

    def get_queryset(self, request):
        return super().get_queryset(request).using(TEAM13_DB)


@admin.register(Place)
class PlaceAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("place_id", "type", "city", "latitude", "longitude")
    list_filter = ("type", "city")
    search_fields = ("city", "address")
    inlines = [PlaceTranslationInline, PlaceAmenityInline]


@admin.register(PlaceTranslation)
class PlaceTranslationAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("place", "lang", "name")
    list_filter = ("lang",)


class EventTranslationInline(admin.TabularInline):
    model = EventTranslation
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).using(TEAM13_DB)


@admin.register(Event)
class EventAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("event_id", "city", "start_at", "end_at")
    list_filter = ("city",)
    inlines = [EventTranslationInline]


@admin.register(EventTranslation)
class EventTranslationAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("event", "lang", "title")
    list_filter = ("lang",)


@admin.register(Image)
class ImageAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("image_id", "target_type", "target_id", "image_url", "is_approved")
    list_filter = ("target_type", "is_approved")
    actions = ["approve_selected_images"]

    @admin.action(description="تأیید تصاویر انتخاب‌شده")
    def approve_selected_images(self, request, queryset):
        n = queryset.using(TEAM13_DB).update(is_approved=True)
        self.message_user(request, f"{n} تصویر تأیید شد.")


@admin.register(Comment)
class CommentAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("comment_id", "target_type", "target_id", "rating", "body_preview", "is_approved", "created_at")
    list_filter = ("target_type", "rating", "is_approved")
    actions = ["approve_selected_comments"]

    def body_preview(self, obj):
        if not obj.body:
            return "—"
        return (obj.body[:50] + "…") if len(obj.body) > 50 else obj.body

    body_preview.short_description = "متن نظر"

    @admin.action(description="تأیید نظرات انتخاب‌شده")
    def approve_selected_comments(self, request, queryset):
        n = queryset.using(TEAM13_DB).update(is_approved=True)
        self.message_user(request, f"{n} نظر تأیید شد.")


@admin.register(HotelDetails)
class HotelDetailsAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("place", "stars", "price_range")


@admin.register(RestaurantDetails)
class RestaurantDetailsAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("place", "cuisine", "avg_price")


@admin.register(MuseumDetails)
class MuseumDetailsAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("place", "open_at", "close_at", "ticket_price")


@admin.register(PlaceAmenity)
class PlaceAmenityAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("place", "amenity_name")
    list_filter = ("amenity_name",)


@admin.register(PlaceContribution)
class PlaceContributionAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("contribution_id", "name_fa", "type", "city", "is_approved", "submitted_by", "created_at")
    list_filter = ("type", "is_approved")
    search_fields = ("name_fa", "name_en", "address")
    readonly_fields = ("contribution_id", "created_at")


@admin.register(TeamAdmin)
class TeamAdminAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("user_id",)


@admin.register(RouteLog)
class RouteLogAdmin(Team13DbAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user_id", "source_place", "destination_place", "travel_mode", "created_at")
    list_filter = ("travel_mode",)
