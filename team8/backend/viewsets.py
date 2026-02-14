"""
Django REST Framework ViewSets for Team 8 APIs
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q
from django.utils import timezone

from .models import (
    Category, Place, Media, Rating, Comment,
    Report, Notification, ActivityLog
)
from .serializers import (
    CategorySerializer, PlaceListSerializer, PlaceDetailSerializer,
    MediaListSerializer, MediaDetailSerializer, MediaUploadSerializer,
    RatingSerializer, CommentSerializer, CommentCreateSerializer,
    ReportSerializer, NotificationSerializer, ActivityLogSerializer
)
from .permissions import IsOwnerOrReadOnly, IsOwner
from .utils import send_to_ai_service, log_activity


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for categories (read-only)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for places
    
    list: Get all places with filtering and search
    retrieve: Get detailed place info with media and comments
    nearby: Get places near a location
    """
    queryset = Place.objects.select_related('category').annotate(
        avg_rating=Avg('ratings__score'),
        media_count=Count('media', filter=Q(media__status='approved')),
        comments_count=Count('comments', filter=Q(comments__status='approved'))
    )
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'avg_rating']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlaceDetailSerializer
        return PlaceListSerializer
    
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Get places near a location
        Query params: lat, lng, radius (km, default 10)
        """
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
            radius = float(request.query_params.get('radius', 10))
        except (TypeError, ValueError):
            return Response(
                {"error": "Invalid lat, lng, or radius"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simple bounding box calculation (for better accuracy, use PostGIS)
        lat_delta = radius / 111  # 1 degree lat ≈ 111km
        lng_delta = radius / (111 * abs(float(lat)))
        
        places = self.get_queryset().filter(
            latitude__gte=lat - lat_delta,
            latitude__lte=lat + lat_delta,
            longitude__gte=lng - lng_delta,
            longitude__lte=lng + lng_delta
        )
        
        serializer = self.get_serializer(places, many=True)
        return Response(serializer.data)


class MediaViewSet(viewsets.ModelViewSet):
    """
    API endpoint for media (photos/videos)
    
    list: Get all approved media
    retrieve: Get media details
    create: Upload new media (sends to AI for moderation)
    update/partial_update: Edit caption
    destroy: Soft delete media
    my_media: Get current user's media
    """
    queryset = Media.objects.select_related('user', 'place').filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['place', 'status', 'mime_type']
    ordering_fields = ['created_at', 'ai_confidence']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MediaUploadSerializer
        elif self.action == 'retrieve':
            return MediaDetailSerializer
        return MediaListSerializer
    
    def get_queryset(self):
        # Non-staff users only see approved media (or their own)
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(status='approved') | Q(user=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Upload media and send to AI service for moderation"""
        # TODO: Upload file to S3/object storage
        # For now, we'll simulate it
        file = self.request.FILES.get('file')
        
        media = serializer.save(
            user=self.request.user,
            s3_object_key=f"media/{timezone.now().timestamp()}_{file.name}",
            bucket_name="team8-media",
            mime_type=file.content_type
        )
        
        # Send to AI service for place recognition
        ai_result = send_to_ai_service(
            endpoint='/recognize-place',
            data={'media_id': str(media.id), 'file_path': media.s3_object_key}
        )
        
        if ai_result and 'confidence' in ai_result:
            media.ai_confidence = ai_result['confidence']
            if ai_result['confidence'] > 0.8:
                media.status = 'approved'
            media.save()
        
        log_activity(self.request.user, 'media_upload', str(media.id))
    
    def perform_update(self, serializer):
        """Mark as edited when caption changes"""
        if 'caption' in serializer.validated_data:
            serializer.save(is_edited=True)
        else:
            serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.deleted_at = timezone.now()
        instance.save()
        log_activity(self.request.user, 'media_delete', str(instance.id))
    
    @action(detail=False, methods=['get'])
    def my_media(self, request):
        """Get current user's media"""
        media = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(media, many=True)
        return Response(serializer.data)


class RatingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for ratings
    
    list: Get all ratings
    create: Rate a place
    update: Update rating
    destroy: Delete rating
    my_ratings: Get current user's ratings
    """
    queryset = Rating.objects.select_related('user', 'place')
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['place']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        log_activity(self.request.user, 'rating_create', str(serializer.instance.place.id))
    
    @action(detail=False, methods=['get'])
    def my_ratings(self, request):
        """Get current user's ratings"""
        ratings = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(ratings, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for comments
    
    list: Get all approved comments
    retrieve: Get comment with replies
    create: Create comment (sends to AI for spam detection)
    update: Edit comment
    destroy: Soft delete comment
    my_comments: Get current user's comments
    """
    queryset = Comment.objects.select_related('user', 'place', 'media', 'parent').filter(
        deleted_at__isnull=True
    )
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['place', 'media', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Non-staff users only see approved comments (or their own)
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(status='approved') | Q(user=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Create comment and send to AI for spam detection"""
        comment = serializer.save(user=self.request.user)
        
        # Send to AI service for spam detection
        ai_result = send_to_ai_service(
            endpoint='/detect-spam',
            data={'comment_id': comment.id, 'content': comment.content}
        )
        
        if ai_result and 'is_spam' in ai_result:
            if not ai_result['is_spam']:
                comment.status = 'approved'
            else:
                comment.status = 'rejected'
                comment.rejection_reason = 'Detected as spam'
            comment.save()
        
        log_activity(self.request.user, 'comment_create', str(comment.id))
    
    def perform_update(self, serializer):
        """Mark as edited"""
        serializer.save(is_edited=True, status='pending')
        
        # Re-check with AI
        comment = serializer.instance
        ai_result = send_to_ai_service(
            endpoint='/detect-spam',
            data={'comment_id': comment.id, 'content': comment.content}
        )
        
        if ai_result and not ai_result.get('is_spam'):
            comment.status = 'approved'
            comment.save()
    
    def perform_destroy(self, instance):
        """Soft delete"""
        instance.deleted_at = timezone.now()
        instance.save()
        log_activity(self.request.user, 'comment_delete', str(instance.id))
    
    @action(detail=False, methods=['get'])
    def my_comments(self, request):
        """Get current user's comments"""
        comments = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)


class ReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for reports
    
    list: Get user's reports (staff see all)
    create: Create report
    """
    queryset = Report.objects.select_related('reporter', 'reported_media', 'reported_comment')
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(reporter=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
        log_activity(self.request.user, 'report_create', str(serializer.instance.id))


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for notifications
    
    list: Get user's notifications
    mark_read: Mark notification as read
    mark_all_read: Mark all notifications as read
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all marked as read'})
