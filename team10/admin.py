from django.contrib import admin
from .models import Trip, TripRequirements, PreferenceConstraint, DailyPlan, HotelSchedule


@admin.register(TripRequirements)
class TripRequirementsAdmin(admin.ModelAdmin):
    """Admin interface for Trip Requirements."""
    list_display = ['id', 'user', 'destination_name', 'start_at', 'end_at', 'budget', 'travelers_count', 'created_at']
    list_filter = ['created_at', 'travelers_count']
    search_fields = ['destination_name', 'user__username']
    date_hierarchy = 'created_at'


@admin.register(PreferenceConstraint)
class PreferenceConstraintAdmin(admin.ModelAdmin):
    """Admin interface for Preference Constraints."""
    list_display = ['id', 'requirements', 'tag', 'description']
    list_filter = ['tag']
    search_fields = ['tag', 'description']


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """Admin interface for Trips."""
    list_display = ['id', 'user', 'status', 'get_destination', 'created_at', 'updated_at', 'get_total_cost']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['user__username', 'requirements__destination_name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at', 'get_total_cost']

    def get_destination(self, obj):
        return obj.requirements.destination_name
    get_destination.short_description = 'Destination'

    def get_total_cost(self, obj):
        return f"{obj.calculate_total_cost():,.0f} تومان"
    get_total_cost.short_description = 'Total Cost'


@admin.register(DailyPlan)
class DailyPlanAdmin(admin.ModelAdmin):
    """Admin interface for Daily Plans."""
    list_display = ['id', 'trip', 'activity_type', 'start_at', 'end_at', 'cost', 'place_source_type']
    list_filter = ['activity_type', 'place_source_type', 'start_at']
    search_fields = ['description', 'trip__id']
    date_hierarchy = 'start_at'


@admin.register(HotelSchedule)
class HotelScheduleAdmin(admin.ModelAdmin):
    """Admin interface for Hotel Schedules."""
    list_display = ['id', 'trip', 'hotel_id', 'start_at', 'end_at', 'rooms_count', 'cost']
    list_filter = ['start_at', 'rooms_count']
    search_fields = ['trip__id', 'hotel_id']
    date_hierarchy = 'start_at'
