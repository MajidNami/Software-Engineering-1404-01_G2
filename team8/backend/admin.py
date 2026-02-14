"""
Django Admin configuration for Team 8 models
"""
from django.contrib import admin
from .models import (
    Category, Place, Media, Rating, Comment,
    Report, Notification, ActivityLog
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'latitude', 'longitude', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'place', 'status', 'mime_type', 'ai_confidence', 'created_at']
    list_filter = ['status', 'mime_type', 'created_at']
    search_fields = ['caption', 'user__email', 'place__title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    actions = ['approve_media', 'reject_media']
    
    def approve_media(self, request, queryset):
        queryset.update(status='approved', rejection_reason='')
    approve_media.short_description = "Approve selected media"
    
    def reject_media(self, request, queryset):
        queryset.update(status='rejected')
    reject_media.short_description = "Reject selected media"


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'place', 'score', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['user__email', 'place__title']
    readonly_fields = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'place', 'status', 'is_edited', 'created_at']
    list_filter = ['status', 'is_edited', 'created_at']
    search_fields = ['content', 'user__email', 'place__title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    actions = ['approve_comments', 'reject_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(status='approved')
    approve_comments.short_description = "Approve selected comments"
    
    def reject_comments(self, request, queryset):
        queryset.update(status='rejected')
    reject_comments.short_description = "Reject selected comments"


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'reporter', 'target_type', 'status', 'created_at']
    list_filter = ['target_type', 'status', 'created_at']
    search_fields = ['reason', 'reporter__email']
    readonly_fields = ['created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['title', 'message', 'user__email']
    readonly_fields = ['created_at']


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'action_type', 'target_id', 'created_at']
    list_filter = ['action_type', 'created_at']
    search_fields = ['user__email', 'action_type', 'target_id']
    readonly_fields = ['created_at']
