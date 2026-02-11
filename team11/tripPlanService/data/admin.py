from django.contrib import admin
from .models import Trip, TripDay, TripItem, ItemDependency, ShareLink, Vote, TripReview, UserMedia


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['trip_id', 'title',
                    'province', 'city', 'status', 'created_at']
    list_filter = ['status', 'budget_level', 'travel_style']
    search_fields = ['title', 'province', 'city']


@admin.register(TripDay)
class TripDayAdmin(admin.ModelAdmin):
    list_display = ['day_id', 'trip', 'day_index', 'specific_date']
    list_filter = ['trip']


@admin.register(TripItem)
class TripItemAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'day', 'item_type',
                    'title', 'start_time', 'end_time']
    list_filter = ['item_type', 'category', 'price_tier']
    search_fields = ['title', 'place_ref_id']


@admin.register(ItemDependency)
class ItemDependencyAdmin(admin.ModelAdmin):
    list_display = ['dependency_id', 'item',
                    'prerequisite_item', 'dependency_type']


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ['link_id', 'trip',
                    'permission', 'expires_at', 'created_at']
    list_filter = ['permission']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['vote_id', 'item', 'is_upvote', 'created_at']
    list_filter = ['is_upvote']


@admin.register(TripReview)
class TripReviewAdmin(admin.ModelAdmin):
    list_display = ['review_id', 'trip', 'rating',
                    'sent_to_central_service', 'created_at']
    list_filter = ['rating', 'sent_to_central_service']


@admin.register(UserMedia)
class UserMediaAdmin(admin.ModelAdmin):
    list_display = ['media_id', 'trip', 'user', 'media_type', 'uploaded_at']
    list_filter = ['media_type']
