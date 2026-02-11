import math

from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.utils import timezone
from django.db.models import Q, Avg, Count

from .models import (
    Province, City, Category, Place, Media, Post, Rating,
    PostVote, Notification, Report,
)
from .serializers import (
    ProvinceSerializer, CitySerializer, CategorySerializer,
    PlaceListSerializer, PlaceDetailSerializer, PlaceCreateSerializer,
    MediaListSerializer, MediaDetailSerializer, MediaUploadSerializer,
    PostListSerializer, PostDetailSerializer, PostCreateSerializer, PostUpdateSerializer,
    RatingSerializer, PostVoteSerializer,
    NotificationSerializer, ReportSerializer,
)
from .permissions import IsAuthenticated, IsOwnerOrReadOnly, AllowAny, IsAdmin
from .storage import storage
from .utils import log_activity, notify_post_owner, create_notification
from . import services


# Read-only reference data

class ProvinceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.select_related('province')
    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['province']
    search_fields = ['name', 'name_en']
    pagination_class = None


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


# Places

class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.select_related('city', 'category')
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'city', 'city__province']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return PlaceCreateSerializer
        if self.action == 'retrieve':
            return PlaceDetailSerializer
        return PlaceListSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        place = serializer.save()
        log_activity(self.request.user, 'PLACE_CREATED', target_id=place.place_id)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius_km = float(request.query_params.get('radius', 10))

        if lat is None or lng is None:
            return Response({'error': 'lat and lng required'}, status=status.HTTP_400_BAD_REQUEST)

        lat = float(lat)
        lng = float(lng)

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0  # Earth radius in km
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)

            a = math.sin(delta_phi / 2) ** 2 + \
                math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2

            return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        qs = []
        for place in self.get_queryset():
            if place.latitude is None or place.longitude is None:
                continue
            if haversine(lat, lng, place.latitude, place.longitude) <= radius_km:
                qs.append(place)

        page = self.paginate_queryset(qs)
        serializer = PlaceListSerializer(page or qs, many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        place = self.get_object()
        agg = place.ratings.aggregate(avg=Avg('score'), count=Count('rating_id'))
        post_count = place.posts.filter(deleted_at__isnull=True, status='APPROVED').count()
        media_count = place.media.filter(deleted_at__isnull=True, status='APPROVED').count()
        return Response({
            'average_rating': agg['avg'],
            'rating_count': agg['count'],
            'post_count': post_count,
            'media_count': media_count,
        })


# Media

class MediaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['place', 'status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Media.objects.select_related('user', 'place').filter(deleted_at__isnull=True)
        if self.action == 'list':
            user = getattr(self.request, 'user', None)
            if user and hasattr(user, 'user_id'):
                qs = qs.filter(Q(status='APPROVED') | Q(user=user))
            else:
                qs = qs.filter(status='APPROVED')
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return MediaUploadSerializer
        if self.action == 'retrieve':
            return MediaDetailSerializer
        return MediaListSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        media = serializer.save()
        # Fire AI moderation + tagging
        services.submit_image_moderation(str(media.media_id), media.s3_object_key)
        services.submit_image_tagging(str(media.media_id), media.s3_object_key)
        log_activity(self.request.user, 'MEDIA_UPLOADED', target_id=str(media.media_id))

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.user_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own media.")
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])
        storage.delete_file(instance.s3_object_key)
        log_activity(self.request.user, 'MEDIA_DELETED', target_id=str(instance.media_id))


# Posts

class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['place', 'parent']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Post.objects.select_related('user', 'place', 'media').filter(deleted_at__isnull=True)
        if self.action == 'list':
            # By default show only top-level posts (not replies)
            if 'parent' not in self.request.query_params:
                qs = qs.filter(parent__isnull=True)
            user = getattr(self.request, 'user', None)
            if user and hasattr(user, 'user_id'):
                qs = qs.filter(Q(status='APPROVED') | Q(user=user))
            else:
                qs = qs.filter(status='APPROVED')
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        if self.action in ('update', 'partial_update'):
            return PostUpdateSerializer
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)

        # Set per-component AI tracking
        post.text_ai_status = 'PENDING_AI'
        if post.media_id:
            post.media_ai_status = 'PENDING_AI'
        post.save(update_fields=['text_ai_status', 'media_ai_status'])

        # Fire AI moderation requests
        services.submit_text_moderation(post.post_id, post.content)
        if post.media and post.media.s3_object_key:
            services.submit_image_moderation(str(post.media.media_id), post.media.s3_object_key)

        log_activity(self.request.user, 'POST_CREATED', target_id=post.post_id)
        if post.parent:
            notify_post_owner(post.parent, self.request.user, 'reply')

    def perform_update(self, serializer):
        post = self.get_object()
        if post.user_id != self.request.user.user_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own posts.")
        serializer.save(is_edited=True)
        log_activity(self.request.user, 'POST_UPDATED', target_id=post.post_id)

    def perform_destroy(self, instance):
        if instance.user_id != self.request.user.user_id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own posts.")
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])
        log_activity(self.request.user, 'POST_DELETED', target_id=instance.post_id)

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        post = self.get_object()
        is_like = request.data.get('is_like')
        if is_like is None:
            return Response({'error': 'is_like required'}, status=status.HTTP_400_BAD_REQUEST)

        vote, created = PostVote.objects.update_or_create(
            user=request.user, post=post,
            defaults={'is_like': bool(is_like)},
        )
        action_type = 'VOTE_CREATED' if created else 'VOTE_UPDATED'
        log_activity(request.user, action_type, target_id=post.post_id)
        notify_post_owner(post, request.user, 'like' if is_like else 'dislike')
        return Response(PostVoteSerializer(vote).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='vote')
    def remove_vote(self, request, pk=None):
        post = self.get_object()
        deleted, _ = PostVote.objects.filter(user=request.user, post=post).delete()
        if not deleted:
            return Response({'error': 'no vote to remove'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        post = self.get_object()
        qs = post.replies.filter(
            deleted_at__isnull=True, status='APPROVED'
        ).select_related('user').order_by('created_at')
        page = self.paginate_queryset(qs)
        serializer = PostListSerializer(page or qs, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)


# Ratings 

class RatingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """One rating per user per place. Create or update via POST/PUT."""
    queryset = Rating.objects.select_related('user', 'place')
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['place']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Create or update rating (upsert)."""
        place_id = request.data.get('place')
        score = request.data.get('score')
        if not place_id or score is None:
            return Response({'error': 'place and score required'}, status=status.HTTP_400_BAD_REQUEST)

        rating, created = Rating.objects.update_or_create(
            user=request.user, place_id=place_id,
            defaults={'score': int(score)},
        )
        action_type = 'RATING_CREATED' if created else 'RATING_UPDATED'
        log_activity(request.user, action_type, target_id=rating.rating_id)
        return Response(
            RatingSerializer(rating).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='my')
    def my_ratings(self, request):
        qs = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# Notifications

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=['post'], url_path='read-all')
    def mark_all_read(self, request):
        count = self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'marked': count})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread': count})


# Reports

class ReportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'target_type']

    def get_queryset(self):
        return Report.objects.filter(reporter=self.request.user).select_related('reporter')

    def perform_create(self, serializer):
        report = serializer.save(reporter=self.request.user)
        log_activity(self.request.user, 'REPORT_CREATED', target_id=report.report_id)

        # Notify the reported content's owner
        if report.target_type == 'POST' and report.reported_post:
            notify_post_owner(report.reported_post, self.request.user, 'report')


# Admin Moderation

class ModerationViewSet(viewsets.GenericViewSet):
    """Admin-only endpoints for reviewing PENDING_ADMIN content."""
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['get'], url_path='posts')
    def pending_posts(self, request):
        """List posts waiting for admin review."""
        qs = Post.objects.filter(
            status='PENDING_ADMIN', deleted_at__isnull=True
        ).select_related('user', 'place', 'media').order_by('created_at')
        page = self.paginate_queryset(qs)
        data = PostListSerializer(page or qs, many=True, context=self.get_serializer_context()).data
        return self.get_paginated_response(data) if page else Response(data)

    @action(detail=False, methods=['get'], url_path='media')
    def pending_media(self, request):
        """List media waiting for admin review."""
        qs = Media.objects.filter(
            status='PENDING_ADMIN', deleted_at__isnull=True
        ).select_related('user', 'place').order_by('created_at')
        page = self.paginate_queryset(qs)
        data = MediaListSerializer(page or qs, many=True, context=self.get_serializer_context()).data
        return self.get_paginated_response(data) if page else Response(data)

    @action(detail=False, methods=['post'], url_path='posts/(?P<post_id>[^/.]+)/approve')
    def approve_post(self, request, post_id=None):
        try:
            post = Post.objects.get(post_id=post_id, status='PENDING_ADMIN')
        except Post.DoesNotExist:
            return Response({'error': 'post not found or not pending'}, status=status.HTTP_404_NOT_FOUND)

        post.status = 'APPROVED'
        post.save(update_fields=['status'])
        log_activity(request.user, 'ADMIN_APPROVED', target_id=post_id)
        create_notification(post.user, 'Post approved', 'Your post has been approved by a moderator.')
        return Response({'post_id': post_id, 'status': 'APPROVED'})

    @action(detail=False, methods=['post'], url_path='posts/(?P<post_id>[^/.]+)/reject')
    def reject_post(self, request, post_id=None):
        try:
            post = Post.objects.get(post_id=post_id, status='PENDING_ADMIN')
        except Post.DoesNotExist:
            return Response({'error': 'post not found or not pending'}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', 'Rejected by admin')
        post.status = 'REJECTED'
        post.rejection_reason = reason
        post.save(update_fields=['status', 'rejection_reason'])
        log_activity(request.user, 'ADMIN_REJECTED', target_id=post_id)
        create_notification(post.user, 'Post rejected', f'Your post was rejected: {reason}')
        return Response({'post_id': post_id, 'status': 'REJECTED'})

    @action(detail=False, methods=['post'], url_path='media/(?P<media_id>[^/.]+)/approve')
    def approve_media(self, request, media_id=None):
        try:
            media = Media.objects.get(media_id=media_id, status='PENDING_ADMIN')
        except Media.DoesNotExist:
            return Response({'error': 'media not found or not pending'}, status=status.HTTP_404_NOT_FOUND)

        media.status = 'APPROVED'
        media.save(update_fields=['status'])
        log_activity(request.user, 'ADMIN_APPROVED', target_id=str(media_id))
        create_notification(media.user, 'Media approved', 'Your media has been approved by a moderator.')

        # Also reconcile any posts referencing this media
        for post in Post.objects.filter(media=media, status='PENDING_ADMIN', deleted_at__isnull=True):
            post.media_ai_status = 'APPROVED'
            post.save(update_fields=['media_ai_status'])
            self._reconcile_admin_post(post, request.user)

        return Response({'media_id': str(media_id), 'status': 'APPROVED'})

    @action(detail=False, methods=['post'], url_path='media/(?P<media_id>[^/.]+)/reject')
    def reject_media(self, request, media_id=None):
        try:
            media = Media.objects.get(media_id=media_id, status='PENDING_ADMIN')
        except Media.DoesNotExist:
            return Response({'error': 'media not found or not pending'}, status=status.HTTP_404_NOT_FOUND)

        reason = request.data.get('reason', 'Rejected by admin')
        media.status = 'REJECTED'
        media.rejection_reason = reason
        media.save(update_fields=['status', 'rejection_reason'])
        log_activity(request.user, 'ADMIN_REJECTED', target_id=str(media_id))
        create_notification(media.user, 'Media rejected', f'Your media was rejected: {reason}')

        # Also reject any posts referencing this media
        for post in Post.objects.filter(media=media, status='PENDING_ADMIN', deleted_at__isnull=True):
            post.media_ai_status = 'REJECTED'
            post.status = 'REJECTED'
            post.rejection_reason = reason
            post.save(update_fields=['media_ai_status', 'status', 'rejection_reason'])
            create_notification(post.user, 'Post rejected', f'Your post was rejected: {reason}')

        return Response({'media_id': str(media_id), 'status': 'REJECTED'})

    @staticmethod
    def _reconcile_admin_post(post, admin_user):
        """After admin approves one component, check if the whole post can be approved."""
        statuses = [post.text_ai_status]
        if post.media_ai_status is not None:
            statuses.append(post.media_ai_status)

        if 'PENDING_ADMIN' in statuses:
            return  # still waiting for another component

        if 'REJECTED' in statuses:
            post.status = 'REJECTED'
        else:
            post.status = 'APPROVED'
        post.save(update_fields=['status'])

        if post.status == 'APPROVED':
            create_notification(post.user, 'Post approved', 'Your post has been approved by a moderator.')
