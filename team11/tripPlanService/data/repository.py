from typing import List, Optional, Dict, Any
from django.db.models import QuerySet, Prefetch, Q
from django.utils import timezone
from datetime import datetime

from .models import (
    Trip, TripDay, TripItem, ItemDependency,
    ShareLink, Vote, TripReview, UserMedia
)


class TripRepository:
    """Repository for Trip model operations"""

    @staticmethod
    def get_all(user_id: Optional[str] = None, status: Optional[str] = None) -> QuerySet[Trip]:
        """Fetch all trips with optional filters"""
        queryset = Trip.objects.select_related(
            'copied_from_trip').all()

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    @staticmethod
    def get_by_id(trip_id: int) -> Optional[Trip]:
        """Fetch a single trip with all related data"""
        return Trip.objects.select_related('copied_from_trip').prefetch_related(
            Prefetch('days', queryset=TripDay.objects.order_by('day_index')),
            'days__items',
            'share_links',
            'reviews',
            'media'
        ).filter(trip_id=trip_id).first()

    @staticmethod
    def create(data: Dict[str, Any]) -> Trip:
        """Create a new trip"""
        return Trip.objects.create(**data)

    @staticmethod
    def update(trip_id: int, data: Dict[str, Any]) -> Optional[Trip]:
        """Update an existing trip"""
        trip = Trip.objects.filter(trip_id=trip_id).first()
        if not trip:
            return None

        for key, value in data.items():
            setattr(trip, key, value)
        trip.save()
        return trip

    @staticmethod
    def delete(trip_id: int) -> bool:
        """Delete a trip"""
        deleted_count, _ = Trip.objects.filter(trip_id=trip_id).delete()
        return deleted_count > 0

    @staticmethod
    def get_by_province(province: str, limit: int = 10) -> QuerySet[Trip]:
        """Get trips by province"""
        return Trip.objects.filter(province=province)[:limit]

    @staticmethod
    def search(query: str) -> QuerySet[Trip]:
        """Search trips by title, province, or city"""
        return Trip.objects.filter(
            Q(title__icontains=query) |
            Q(province__icontains=query) |
            Q(city__icontains=query)
        )


class TripDayRepository:
    """Repository for TripDay model operations"""

    @staticmethod
    def get_by_trip(trip_id: int) -> QuerySet[TripDay]:
        """Get all days for a specific trip"""
        return TripDay.objects.filter(trip_id=trip_id).prefetch_related(
            'items'
        ).order_by('day_index')

    @staticmethod
    def get_by_id(day_id: int) -> Optional[TripDay]:
        """Get a specific day with items"""
        return TripDay.objects.prefetch_related('items').filter(
            day_id=day_id
        ).first()

    @staticmethod
    def create(data: Dict[str, Any]) -> TripDay:
        """Create a new trip day"""
        return TripDay.objects.create(**data)

    @staticmethod
    def update(day_id: int, data: Dict[str, Any]) -> Optional[TripDay]:
        """Update a trip day"""
        day = TripDay.objects.filter(day_id=day_id).first()
        if not day:
            return None

        for key, value in data.items():
            setattr(day, key, value)
        day.save()
        return day

    @staticmethod
    def delete(day_id: int) -> bool:
        """Delete a trip day"""
        deleted_count, _ = TripDay.objects.filter(day_id=day_id).delete()
        return deleted_count > 0

    @staticmethod
    def bulk_create_for_trip(trip: Trip, days_data: List[Dict[str, Any]]) -> List[TripDay]:
        """Create multiple days for a trip in one operation"""
        days = [TripDay(trip=trip, **data) for data in days_data]
        return TripDay.objects.bulk_create(days)


class TripItemRepository:
    """Repository for TripItem model operations"""

    @staticmethod
    def get_by_day(day_id: int) -> QuerySet[TripItem]:
        """Get all items for a specific day"""
        return TripItem.objects.filter(day_id=day_id).order_by('sort_order')

    @staticmethod
    def get_by_id(item_id: int) -> Optional[TripItem]:
        """Get a specific item"""
        return TripItem.objects.select_related('day__trip').filter(
            item_id=item_id
        ).first()

    @staticmethod
    def create(data: Dict[str, Any]) -> TripItem:
        """Create a new trip item"""
        return TripItem.objects.create(**data)

    @staticmethod
    def update(item_id: int, data: Dict[str, Any]) -> Optional[TripItem]:
        """Update a trip item"""
        item = TripItem.objects.filter(item_id=item_id).first()
        if not item:
            return None

        for key, value in data.items():
            setattr(item, key, value)
        item.save()
        return item

    @staticmethod
    def delete(item_id: int) -> bool:
        """Delete a trip item"""
        deleted_count, _ = TripItem.objects.filter(item_id=item_id).delete()
        return deleted_count > 0

    @staticmethod
    def reorder_items(day_id: int, item_order: List[int]) -> bool:
        """Reorder items in a day based on provided order"""
        items = TripItem.objects.filter(day_id=day_id, item_id__in=item_order)

        for index, item_id in enumerate(item_order):
            items.filter(item_id=item_id).update(sort_order=index)

        return True

    @staticmethod
    def get_locked_items(day_id: int) -> QuerySet[TripItem]:
        """Get all locked items in a day"""
        return TripItem.objects.filter(day_id=day_id, is_locked=True)


class ItemDependencyRepository:
    """Repository for ItemDependency model operations"""

    @staticmethod
    def get_by_item(item_id: int) -> QuerySet[ItemDependency]:
        """Get all dependencies for an item"""
        return ItemDependency.objects.filter(item_id=item_id).select_related(
            'prerequisite_item'
        )

    @staticmethod
    def get_prerequisites(item_id: int) -> QuerySet[TripItem]:
        """Get all prerequisite items"""
        dependencies = ItemDependency.objects.filter(item_id=item_id).select_related(
            'prerequisite_item'
        )
        return [dep.prerequisite_item for dep in dependencies]

    @staticmethod
    def create(data: Dict[str, Any]) -> ItemDependency:
        """Create a new dependency"""
        return ItemDependency.objects.create(**data)

    @staticmethod
    def delete(dependency_id: int) -> bool:
        """Delete a dependency"""
        deleted_count, _ = ItemDependency.objects.filter(
            dependency_id=dependency_id
        ).delete()
        return deleted_count > 0

    @staticmethod
    def check_circular_dependency(item_id: int, prerequisite_id: int) -> bool:
        """Check if adding a dependency would create a cycle"""
        visited = set()

        def has_path(current: int, target: int) -> bool:
            if current == target:
                return True
            if current in visited:
                return False

            visited.add(current)
            dependencies = ItemDependency.objects.filter(
                prerequisite_item_id=current
            ).values_list('item_id', flat=True)

            return any(has_path(dep, target) for dep in dependencies)

        return has_path(prerequisite_id, item_id)


class ShareLinkRepository:
    """Repository for ShareLink model operations"""

    @staticmethod
    def get_by_trip(trip_id: int) -> QuerySet[ShareLink]:
        """Get all share links for a trip"""
        return ShareLink.objects.filter(trip_id=trip_id).order_by('-created_at')

    @staticmethod
    def get_by_token(token: str) -> Optional[ShareLink]:
        """Get a share link by token"""
        return ShareLink.objects.select_related('trip').filter(
            token=token,
            expires_at__gt=timezone.now()
        ).first()

    @staticmethod
    def create(data: Dict[str, Any]) -> ShareLink:
        """Create a new share link"""
        return ShareLink.objects.create(**data)

    @staticmethod
    def delete(link_id: int) -> bool:
        """Delete a share link"""
        deleted_count, _ = ShareLink.objects.filter(link_id=link_id).delete()
        return deleted_count > 0

    @staticmethod
    def cleanup_expired(trip_id: Optional[int] = None) -> int:
        """Delete expired share links"""
        queryset = ShareLink.objects.filter(expires_at__lt=timezone.now())
        if trip_id:
            queryset = queryset.filter(trip_id=trip_id)

        deleted_count, _ = queryset.delete()
        return deleted_count


class VoteRepository:
    """Repository for Vote model operations"""

    @staticmethod
    def get_by_item(item_id: int) -> QuerySet[Vote]:
        """Get all votes for an item"""
        return Vote.objects.filter(item_id=item_id)

    @staticmethod
    def get_vote_count(item_id: int) -> Dict[str, int]:
        """Get upvote and downvote counts for an item"""
        votes = Vote.objects.filter(item_id=item_id)
        upvotes = votes.filter(is_upvote=True).count()
        downvotes = votes.filter(is_upvote=False).count()

        return {
            'upvotes': upvotes,
            'downvotes': downvotes,
            'total': upvotes - downvotes
        }

    @staticmethod
    def get_user_vote(item_id: int, session_id: str) -> Optional[Vote]:
        """Get a specific user's vote on an item"""
        return Vote.objects.filter(
            item_id=item_id,
            guest_session_id=session_id
        ).first()

    @staticmethod
    def create_or_update(data: Dict[str, Any]) -> Vote:
        """Create or update a vote"""
        vote, created = Vote.objects.update_or_create(
            item_id=data['item_id'],
            guest_session_id=data['guest_session_id'],
            defaults={'is_upvote': data['is_upvote']}
        )
        return vote

    @staticmethod
    def delete(vote_id: int) -> bool:
        """Delete a vote"""
        deleted_count, _ = Vote.objects.filter(vote_id=vote_id).delete()
        return deleted_count > 0


class TripReviewRepository:
    """Repository for TripReview model operations"""

    @staticmethod
    def get_by_trip(trip_id: int) -> QuerySet[TripReview]:
        """Get all reviews for a trip"""
        return TripReview.objects.filter(trip_id=trip_id).order_by('-created_at')

    @staticmethod
    def get_by_item(item_id: int) -> QuerySet[TripReview]:
        """Get all reviews for a specific item"""
        return TripReview.objects.filter(item_id=item_id).order_by('-created_at')

    @staticmethod
    def create(data: Dict[str, Any]) -> TripReview:
        """Create a new review"""
        return TripReview.objects.create(**data)

    @staticmethod
    def update(review_id: int, data: Dict[str, Any]) -> Optional[TripReview]:
        """Update a review"""
        review = TripReview.objects.filter(review_id=review_id).first()
        if not review:
            return None

        for key, value in data.items():
            setattr(review, key, value)
        review.save()
        return review

    @staticmethod
    def delete(review_id: int) -> bool:
        """Delete a review"""
        deleted_count, _ = TripReview.objects.filter(
            review_id=review_id).delete()
        return deleted_count > 0

    @staticmethod
    def get_average_rating(trip_id: int) -> Optional[float]:
        """Calculate average rating for a trip"""
        from django.db.models import Avg
        result = TripReview.objects.filter(trip_id=trip_id).aggregate(
            avg_rating=Avg('rating')
        )
        return result['avg_rating']

    @staticmethod
    def mark_as_sent(review_id: int) -> bool:
        """Mark review as sent to central service"""
        updated = TripReview.objects.filter(review_id=review_id).update(
            sent_to_central_service=True
        )
        return updated > 0


class UserMediaRepository:
    """Repository for UserMedia model operations"""

    @staticmethod
    def get_by_trip(trip_id: int) -> QuerySet[UserMedia]:
        """Get all media for a trip"""
        return UserMedia.objects.filter(trip_id=trip_id).order_by('-uploaded_at')

    @staticmethod
    def get_by_user(user_id: str, trip_id: Optional[int] = None) -> QuerySet[UserMedia]:
        """Get all media uploaded by a user"""
        queryset = UserMedia.objects.filter(user_id=user_id)
        if trip_id:
            queryset = queryset.filter(trip_id=trip_id)
        return queryset.order_by('-uploaded_at')

    @staticmethod
    def create(data: Dict[str, Any]) -> UserMedia:
        """Upload new media"""
        return UserMedia.objects.create(**data)

    @staticmethod
    def delete(media_id: int) -> bool:
        """Delete media"""
        deleted_count, _ = UserMedia.objects.filter(media_id=media_id).delete()
        return deleted_count > 0

    @staticmethod
    def get_by_type(trip_id: int, media_type: str) -> QuerySet[UserMedia]:
        """Get media by type for a trip"""
        return UserMedia.objects.filter(
            trip_id=trip_id,
            media_type=media_type
        ).order_by('-uploaded_at')
