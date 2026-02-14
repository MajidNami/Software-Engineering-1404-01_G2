"""
Django REST Framework Serializers for Team 8 models
"""
from rest_framework import serializers
from .models import (
    Category, Place, Media, Rating, Comment, 
    Report, Notification, ActivityLog
)


class CategorySerializer(serializers.ModelSerializer):
    places_count = serializers.IntegerField(source='places.count', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'places_count']


class PlaceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for place lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    avg_rating = serializers.SerializerMethodField()
    media_count = serializers.IntegerField(source='media.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    
    class Meta:
        model = Place
        fields = [
            'id', 'title', 'description', 'latitude', 'longitude',
            'category', 'category_name', 'avg_rating', 
            'media_count', 'comments_count', 'created_at'
        ]
    
    def get_avg_rating(self, obj):
        from django.db.models import Avg
        result = obj.ratings.aggregate(Avg('score'))
        return round(result['score__avg'], 2) if result['score__avg'] else None


class PlaceDetailSerializer(PlaceListSerializer):
    """Detailed serializer with related data"""
    recent_media = serializers.SerializerMethodField()
    recent_comments = serializers.SerializerMethodField()
    
    class Meta(PlaceListSerializer.Meta):
        fields = PlaceListSerializer.Meta.fields + ['recent_media', 'recent_comments']
    
    def get_recent_media(self, obj):
        media = obj.media.filter(status='approved')[:5]
        return MediaListSerializer(media, many=True).data
    
    def get_recent_comments(self, obj):
        comments = obj.comments.filter(status='approved', parent=None)[:5]
        return CommentSerializer(comments, many=True).data


class MediaListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for media lists"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    place_title = serializers.CharField(source='place.title', read_only=True)
    
    class Meta:
        model = Media
        fields = [
            'id', 'user', 'user_email', 'place', 'place_title',
            's3_object_key', 'mime_type', 'caption', 'status',
            'ai_confidence', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'ai_confidence', 'created_at']


class MediaDetailSerializer(MediaListSerializer):
    """Detailed serializer with comments"""
    comments = serializers.SerializerMethodField()
    
    class Meta(MediaListSerializer.Meta):
        fields = MediaListSerializer.Meta.fields + [
            'is_edited', 'rejection_reason', 'updated_at', 'comments'
        ]
    
    def get_comments(self, obj):
        comments = obj.comments.filter(status='approved')[:20]
        return CommentSerializer(comments, many=True).data


class MediaUploadSerializer(serializers.ModelSerializer):
    """Serializer for media upload"""
    file = serializers.FileField(write_only=True)
    
    class Meta:
        model = Media
        fields = ['place', 'caption', 'file']
    
    def validate_file(self, file):
        from .settings import MAX_UPLOAD_SIZE, ALLOWED_IMAGE_TYPES, ALLOWED_VIDEO_TYPES
        
        if file.size > MAX_UPLOAD_SIZE:
            raise serializers.ValidationError(
                f"File size must be under {MAX_UPLOAD_SIZE / (1024*1024)}MB"
            )
        
        mime_type = file.content_type
        if mime_type not in ALLOWED_IMAGE_TYPES + ALLOWED_VIDEO_TYPES:
            raise serializers.ValidationError(
                f"File type {mime_type} not allowed"
            )
        
        return file


class RatingSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    place_title = serializers.CharField(source='place.title', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'user', 'user_email', 'place', 'place_title', 'score', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def validate_score(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Score must be between 1 and 5")
        return value
    
    def create(self, validated_data):
        # Update or create rating
        user = validated_data['user']
        place = validated_data['place']
        
        rating, created = Rating.objects.update_or_create(
            user=user,
            place=place,
            defaults={'score': validated_data['score']}
        )
        return rating


class CommentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    place_title = serializers.CharField(source='place.title', read_only=True)
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'user_email', 'user_name', 'place', 'place_title',
            'media', 'parent', 'content', 'status', 'is_edited',
            'replies_count', 'replies', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'is_edited', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.email
    
    def get_replies(self, obj):
        # Only show top-level replies, prevent infinite recursion
        if obj.parent is None:
            replies = obj.replies.filter(status='approved')[:10]
            return CommentSerializer(replies, many=True, context={'no_replies': True}).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['place', 'media', 'parent', 'content']
    
    def validate(self, data):
        # Can't comment on both place and media
        if not data.get('place') and not data.get('media'):
            raise serializers.ValidationError("Must specify either place or media")
        
        # If replying, check parent exists
        if data.get('parent'):
            parent = data['parent']
            if parent.status != 'approved':
                raise serializers.ValidationError("Cannot reply to unapproved comment")
        
        return data


class ReportSerializer(serializers.ModelSerializer):
    reporter_email = serializers.EmailField(source='reporter.email', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'reporter_email', 'target_type',
            'reported_media', 'reported_comment', 'reason',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'reporter', 'status', 'created_at']
    
    def validate(self, data):
        target_type = data.get('target_type')
        
        if target_type == 'media' and not data.get('reported_media'):
            raise serializers.ValidationError("Must specify reported_media for media reports")
        
        if target_type == 'comment' and not data.get('reported_comment'):
            raise serializers.ValidationError("Must specify reported_comment for comment reports")
        
        return data


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class ActivityLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_email', 'action_type', 'target_id', 'metadata', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
