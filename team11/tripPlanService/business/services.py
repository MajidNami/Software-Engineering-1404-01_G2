from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import secrets

from data.repository import (
    TripRepository, TripDayRepository, TripItemRepository,
    ItemDependencyRepository, ShareLinkRepository, VoteRepository,
    TripReviewRepository, UserMediaRepository
)
from data.models import (
    Trip, TripDay, TripItem, ItemDependency,
    ShareLink, Vote, TripReview, UserMedia
)


class TripService:
    """Business logic for Trip operations"""
    
    @staticmethod
    def get_all_trips(user_id: Optional[int] = None, status: Optional[str] = None) -> List[Trip]:
        """Get all trips with optional filters"""
        return list(TripRepository.get_all(user_id, status))
    
    @staticmethod
    def get_trip_detail(trip_id: int) -> Optional[Trip]:
        """Get detailed trip information"""
        return TripRepository.get_by_id(trip_id)
    
    @staticmethod
    def create_trip(user_id: Optional[int], data: Dict[str, Any]) -> Trip:
        """Create a new trip with validation"""
        if not data.get('title'):
            raise ValueError("Trip title is required")
        if not data.get('province'):
            raise ValueError("Province is required")
        if not data.get('start_date'):
            raise ValueError("Start date is required")
        if not data.get('duration_days') or data['duration_days'] < 1:
            raise ValueError("Duration must be at least 1 day")
        
        trip_data = {**data}
        if user_id:
            trip_data['user_id'] = user_id
            
        return TripRepository.create(trip_data)
    
    @staticmethod
    def update_trip(trip_id: int, data: Dict[str, Any]) -> Optional[Trip]:
        """Update trip information"""
        trip = TripRepository.get_by_id(trip_id)
        if not trip:
            return None
            
        return TripRepository.update(trip_id, data)
    
    @staticmethod
    def delete_trip(trip_id: int) -> bool:
        """Delete a trip"""
        return TripRepository.delete(trip_id)
    
    @staticmethod
    def copy_trip(trip_id: int, user_id: Optional[int] = None) -> Optional[Trip]:
        """Create a copy of an existing trip"""
        original = TripRepository.get_by_id(trip_id)
        if not original:
            return None
        
        new_trip_data = {
            'user_id': user_id,
            'copied_from_trip_id': trip_id,
            'title': f"{original.title} (Copy)",
            'province': original.province,
            'city': original.city,
            'start_date': original.start_date,
            'duration_days': original.duration_days,
            'budget_level': original.budget_level,
            'daily_available_hours': original.daily_available_hours,
            'travel_style': original.travel_style,
            'generation_strategy': original.generation_strategy,
        }
        
        return TripRepository.create(new_trip_data)
    
    @staticmethod
    def finalize_trip(trip_id: int) -> Optional[Trip]:
        """Finalize a trip (change status from DRAFT to FINALIZED)"""
        return TripRepository.update(trip_id, {'status': 'FINALIZED'})
    
    @staticmethod
    def search_trips(query: str) -> List[Trip]:
        """Search trips by title, province, or city"""
        return list(TripRepository.search(query))


class TripDayService:
    """Business logic for TripDay operations"""
    
    @staticmethod
    def get_days_for_trip(trip_id: int) -> List[TripDay]:
        """Get all days for a trip"""
        return list(TripDayRepository.get_by_trip(trip_id))
    
    @staticmethod
    def create_day(trip_id: int, data: Dict[str, Any]) -> TripDay:
        """Create a new day for a trip"""
        day_data = {**data, 'trip_id': trip_id}
        return TripDayRepository.create(day_data)
    
    @staticmethod
    def update_day(day_id: int, data: Dict[str, Any]) -> Optional[TripDay]:
        """Update a trip day"""
        return TripDayRepository.update(day_id, data)
    
    @staticmethod
    def delete_day(day_id: int) -> bool:
        """Delete a trip day"""
        return TripDayRepository.delete(day_id)
    
    @staticmethod
    def generate_days_for_trip(trip: Trip) -> List[TripDay]:
        """Auto-generate days based on trip duration"""
        days_data = []
        for i in range(trip.duration_days):
            day_date = trip.start_date + timedelta(days=i)
            days_data.append({
                'day_index': i + 1,
                'specific_date': day_date,
            })
        
        return TripDayRepository.bulk_create_for_trip(trip, days_data)


class TripItemService:
    """Business logic for TripItem operations"""
    
    @staticmethod
    def get_items_for_day(day_id: int) -> List[TripItem]:
        """Get all items for a specific day"""
        return list(TripItemRepository.get_by_day(day_id))
    
    @staticmethod
    def create_item(day_id: int, data: Dict[str, Any]) -> TripItem:
        """Create a new item for a day"""
        if not data.get('place_ref_id'):
            raise ValueError("Place reference ID is required")
        if not data.get('title'):
            raise ValueError("Item title is required")
            
        item_data = {**data, 'day_id': day_id}
        return TripItemRepository.create(item_data)
    
    @staticmethod
    def update_item(item_id: int, data: Dict[str, Any]) -> Optional[TripItem]:
        """Update a trip item"""
        item = TripItemRepository.get_by_id(item_id)
        if not item:
            return None
            
        if item.is_locked and 'start_time' in data:
            raise ValueError("Cannot modify time of locked item")
            
        return TripItemRepository.update(item_id, data)
    
    @staticmethod
    def delete_item(item_id: int) -> bool:
        """Delete a trip item"""
        return TripItemRepository.delete(item_id)
    
    @staticmethod
    def lock_item(item_id: int) -> Optional[TripItem]:
        """Lock an item to prevent time changes"""
        return TripItemRepository.update(item_id, {'is_locked': True})
    
    @staticmethod
    def unlock_item(item_id: int) -> Optional[TripItem]:
        """Unlock an item"""
        return TripItemRepository.update(item_id, {'is_locked': False})
    
    @staticmethod
    def reorder_items(day_id: int, item_order: List[int]) -> bool:
        """Reorder items in a day"""
        return TripItemRepository.reorder_items(day_id, item_order)


class DependencyService:
    """Business logic for ItemDependency operations"""
    
    @staticmethod
    def add_dependency(item_id: int, prerequisite_id: int, 
                      dependency_type: str = 'FINISH_TO_START') -> ItemDependency:
        """Add a dependency between items"""
        if ItemDependencyRepository.check_circular_dependency(item_id, prerequisite_id):
            raise ValueError("Cannot add dependency: would create a circular dependency")
        
        return ItemDependencyRepository.create({
            'item_id': item_id,
            'prerequisite_item_id': prerequisite_id,
            'dependency_type': dependency_type
        })
    
    @staticmethod
    def remove_dependency(dependency_id: int) -> bool:
        """Remove a dependency"""
        return ItemDependencyRepository.delete(dependency_id)
    
    @staticmethod
    def get_item_dependencies(item_id: int) -> List:
        """Get all dependencies for an item"""
        return list(ItemDependencyRepository.get_by_item(item_id))


class ShareService:
    """Business logic for ShareLink operations"""
    
    @staticmethod
    def create_share_link(trip_id: int, permission: str = 'VIEW', 
                         expires_in_hours: int = 168) -> ShareLink:
        """Create a shareable link for a trip"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        
        return ShareLinkRepository.create({
            'trip_id': trip_id,
            'token': token,
            'expires_at': expires_at,
            'permission': permission
        })
    
    @staticmethod
    def get_trip_by_token(token: str) -> Optional[Trip]:
        """Get trip using share token"""
        share_link = ShareLinkRepository.get_by_token(token)
        return share_link.trip if share_link else None
    
    @staticmethod
    def revoke_link(link_id: int) -> bool:
        """Revoke a share link"""
        return ShareLinkRepository.delete(link_id)
    
    @staticmethod
    def cleanup_expired_links(trip_id: Optional[int] = None) -> int:
        """Remove expired share links"""
        return ShareLinkRepository.cleanup_expired(trip_id)


class VotingService:
    """Business logic for Vote operations"""
    
    @staticmethod
    def cast_vote(item_id: int, session_id: str, is_upvote: bool) -> Vote:
        """Cast or update a vote on an item"""
        return VoteRepository.create_or_update({
            'item_id': item_id,
            'guest_session_id': session_id,
            'is_upvote': is_upvote
        })
    
    @staticmethod
    def get_vote_summary(item_id: int) -> Dict[str, int]:
        """Get vote statistics for an item"""
        return VoteRepository.get_vote_count(item_id)
    
    @staticmethod
    def remove_vote(vote_id: int) -> bool:
        """Remove a vote"""
        return VoteRepository.delete(vote_id)


class ReviewService:
    """Business logic for TripReview operations"""
    
    @staticmethod
    def create_review(trip_id: int, rating: int, comment: str = "",
                     item_id: Optional[int] = None) -> TripReview:
        """Create a review for a trip or specific item"""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        return TripReviewRepository.create({
            'trip_id': trip_id,
            'item_id': item_id,
            'rating': rating,
            'comment': comment
        })
    
    @staticmethod
    def get_trip_reviews(trip_id: int) -> List[TripReview]:
        """Get all reviews for a trip"""
        return list(TripReviewRepository.get_by_trip(trip_id))
    
    @staticmethod
    def get_average_rating(trip_id: int) -> Optional[float]:
        """Get average rating for a trip"""
        return TripReviewRepository.get_average_rating(trip_id)
    
    @staticmethod
    def update_review(review_id: int, data: Dict[str, Any]) -> Optional[TripReview]:
        """Update a review"""
        return TripReviewRepository.update(review_id, data)
    
    @staticmethod
    def delete_review(review_id: int) -> bool:
        """Delete a review"""
        return TripReviewRepository.delete(review_id)


class MediaService:
    """Business logic for UserMedia operations"""
    
    @staticmethod
    def upload_media(trip_id: int, user_id: int, media_url: str,
                    caption: str = "", media_type: str = 'PHOTO') -> UserMedia:
        """Upload media for a trip"""
        return UserMediaRepository.create({
            'trip_id': trip_id,
            'user_id': user_id,
            'media_url': media_url,
            'caption': caption,
            'media_type': media_type
        })
    
    @staticmethod
    def get_trip_media(trip_id: int) -> List[UserMedia]:
        """Get all media for a trip"""
        return list(UserMediaRepository.get_by_trip(trip_id))
    
    @staticmethod
    def get_user_media(user_id: int, trip_id: Optional[int] = None) -> List[UserMedia]:
        """Get all media uploaded by a user"""
        return list(UserMediaRepository.get_by_user(user_id, trip_id))
    
    @staticmethod
    def delete_media(media_id: int) -> bool:
        """Delete media"""
        return UserMediaRepository.delete(media_id)
