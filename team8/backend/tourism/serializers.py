from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.conf import settings
from .models import (
    User, Province, City, Category, Place, Media, Post, Rating,
    PostVote, Notification, Report,
)
from .storage import storage


# Reference Data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'is_admin', 'created_at']
        read_only_fields = fields


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['province_id', 'name', 'name_en']


class CitySerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source='province.name', read_only=True)

    class Meta:
        model = City
        fields = ['city_id', 'province', 'province_name', 'name', 'name_en']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'name', 'name_en']


# Place

class PlaceListSerializer(GeoFeatureModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    average_rating = serializers.ReadOnlyField()
    rating_count = serializers.ReadOnlyField()

    class Meta:
        model = Place
        geo_field = 'location'
        fields = [
            'place_id', 'title', 'description', 'city', 'city_name',
            'category', 'category_name', 'average_rating', 'rating_count',
            'created_at',
        ]


class PlaceDetailSerializer(PlaceListSerializer):
    recent_media = serializers.SerializerMethodField()
    recent_posts = serializers.SerializerMethodField()

    class Meta(PlaceListSerializer.Meta):
        fields = PlaceListSerializer.Meta.fields + ['recent_media', 'recent_posts']

    def get_recent_media(self, obj):
        qs = obj.media.filter(status='APPROVED', deleted_at__isnull=True)[:6]
        return MediaListSerializer(qs, many=True, context=self.context).data

    def get_recent_posts(self, obj):
        qs = obj.posts.filter(
            status='APPROVED', deleted_at__isnull=True, parent__isnull=True
        ).select_related('user')[:10]
        return PostListSerializer(qs, many=True, context=self.context).data


class PlaceCreateSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = Place
        fields = ['title', 'description', 'city', 'category', 'latitude', 'longitude']

    def create(self, validated_data):
        lat = validated_data.pop('latitude', None)
        lng = validated_data.pop('longitude', None)
        if lat is not None and lng is not None:
            from django.contrib.gis.geos import Point
            validated_data['location'] = Point(lng, lat, srid=4326)
        return super().create(validated_data)


# Media

class MediaListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    place_title = serializers.CharField(source='place.title', read_only=True)
    url = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = [
            'media_id', 'user', 'username', 'place', 'place_title',
            'mime_type', 'status', 'url', 'created_at',
        ]
        read_only_fields = ['media_id', 'status', 'created_at']

    def get_url(self, obj):
        return storage.get_presigned_url(obj.s3_object_key)


class MediaDetailSerializer(MediaListSerializer):
    class Meta(MediaListSerializer.Meta):
        fields = MediaListSerializer.Meta.fields + [
            'ai_confidence', 'rejection_reason', 'updated_at',
        ]


class MediaUploadSerializer(serializers.Serializer):
    """Handles actual file upload to MinIO."""
    file = serializers.FileField()
    place = serializers.PrimaryKeyRelatedField(queryset=Place.objects.all())

    def validate_file(self, value):
        from .utils import validate_upload
        err = validate_upload(value)
        if err:
            raise serializers.ValidationError(err)
        return value

    def create(self, validated_data):
        file = validated_data['file']
        place = validated_data['place']
        user = self.context['request'].user

        result = storage.upload_file(file, folder=f"places/{place.place_id}")

        return Media.objects.create(
            user=user,
            place=place,
            s3_object_key=result['s3_object_key'],
            bucket_name=result['bucket_name'],
            mime_type=result['mime_type'],
        )


# Post 

class PostListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    like_count = serializers.ReadOnlyField()
    dislike_count = serializers.ReadOnlyField()
    reply_count = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = [
            'post_id', 'user', 'username', 'place', 'parent', 'media',
            'content', 'is_edited', 'status',
            'like_count', 'dislike_count', 'reply_count', 'created_at',
        ]
        read_only_fields = [
            'post_id', 'user', 'is_edited', 'status',
            'like_count', 'dislike_count', 'reply_count', 'created_at',
        ]


class PostDetailSerializer(PostListSerializer):
    replies = serializers.SerializerMethodField()
    media_detail = MediaListSerializer(source='media', read_only=True)
    user_vote = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + [
            'replies', 'media_detail', 'user_vote', 'updated_at',
        ]

    def get_replies(self, obj):
        qs = obj.replies.filter(
            deleted_at__isnull=True, status='APPROVED'
        ).select_related('user').order_by('created_at')
        return PostListSerializer(qs, many=True, context=self.context).data

    def get_user_vote(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not hasattr(request.user, 'user_id'):
            return None
        vote = PostVote.objects.filter(user=request.user, post=obj).first()
        return vote.is_like if vote else None


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['place', 'parent', 'media', 'content']

    def validate_parent(self, value):
        if value and value.deleted_at:
            raise serializers.ValidationError("Cannot reply to a deleted post.")
        return value

    def validate(self, data):
        parent = data.get('parent')
        if parent and parent.place_id != data['place'].place_id:
            raise serializers.ValidationError("Reply must be in the same place as parent.")
        return data


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['content']


# Rating

class RatingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Rating
        fields = ['rating_id', 'user', 'username', 'place', 'score', 'created_at']
        read_only_fields = ['rating_id', 'user', 'created_at']

    def validate_score(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Score must be 1-5.")
        return value


# PostVote

class PostVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVote
        fields = ['vote_id', 'user', 'post', 'is_like', 'created_at']
        read_only_fields = ['vote_id', 'user', 'created_at']


# Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['notification_id', 'title', 'message', 'is_read', 'created_at']
        read_only_fields = fields


# Report

class ReportSerializer(serializers.ModelSerializer):
    reporter_username = serializers.CharField(source='reporter.username', read_only=True)

    class Meta:
        model = Report
        fields = [
            'report_id', 'reporter', 'reporter_username', 'target_type',
            'reported_media', 'reported_post', 'reason', 'status', 'created_at',
        ]
        read_only_fields = ['report_id', 'reporter', 'status', 'created_at']

    def validate(self, data):
        tt = data.get('target_type')
        if tt == 'MEDIA' and not data.get('reported_media'):
            raise serializers.ValidationError("reported_media required for MEDIA reports.")
        if tt == 'POST' and not data.get('reported_post'):
            raise serializers.ValidationError("reported_post required for POST reports.")
        if tt == 'MEDIA':
            data['reported_post'] = None
        elif tt == 'POST':
            data['reported_media'] = None
        return data
