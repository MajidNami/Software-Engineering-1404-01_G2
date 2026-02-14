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

from externalServices.grpc.services.facility_client import FacilityClient
from externalServices.grpc.services.recommendation_client import RecommendationClient
from externalServices.grpc.services.wiki_client import WikiClient

class TripService:
    """Business logic for Trip operations"""

    @staticmethod
    def get_all_trips(user_id: Optional[str] = None, status: Optional[str] = None) -> List[Trip]:
        """Get all trips with optional filters"""
        return list(TripRepository.get_all(user_id, status))

    @staticmethod
    def get_trip_detail(trip_id: int) -> Optional[Trip]:
        """Get detailed trip information"""
        return TripRepository.get_by_id(trip_id)

    @staticmethod
    def create_trip(user_id: Optional[str], data: Dict[str, Any]) -> Trip:
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
    def copy_trip(trip_id: int, user_id: Optional[str] = None) -> Optional[Trip]:
        """Create a deep copy of an existing trip (including days and items)"""
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
            'end_date': original.end_date,
            'duration_days': original.duration_days,
            'budget_level': original.budget_level,
            'daily_available_hours': original.daily_available_hours,
            'travel_style': original.travel_style,
            'generation_strategy': original.generation_strategy,
            'density': original.density,
            'interests': original.interests,
            'total_estimated_cost': original.total_estimated_cost,
        }

        new_trip = TripRepository.create(new_trip_data)

        # Deep copy: duplicate days and items
        for day in original.days.all().order_by('day_index'):
            new_day = TripDayRepository.create({
                'trip_id': new_trip.trip_id,
                'day_index': day.day_index,
                'specific_date': day.specific_date,
                'start_geo_location': day.start_geo_location,
            })

            for item in day.items.all().order_by('sort_order'):
                TripItemRepository.create({
                    'day_id': new_day.day_id,
                    'item_type': item.item_type,
                    'place_ref_id': item.place_ref_id,
                    'title': item.title,
                    'category': item.category,
                    'address_summary': item.address_summary,
                    'lat': item.lat,
                    'lng': item.lng,
                    'wiki_summary': item.wiki_summary,
                    'wiki_link': item.wiki_link,
                    'main_image_url': item.main_image_url,
                    'start_time': item.start_time,
                    'end_time': item.end_time,
                    'duration_minutes': item.duration_minutes,
                    'sort_order': item.sort_order,
                    'is_locked': False,  # Unlock copied items
                    'price_tier': item.price_tier,
                    'estimated_cost': item.estimated_cost,
                    'transport_mode_to_next': item.transport_mode_to_next,
                    'travel_time_to_next': item.travel_time_to_next,
                    'travel_distance_to_next': item.travel_distance_to_next,
                })

        return TripRepository.get_by_id(new_trip.trip_id)

    @staticmethod
    def finalize_trip(trip_id: int) -> Optional[Trip]:
        """Finalize a trip (change status from DRAFT to FINALIZED)"""
        return TripRepository.update(trip_id, {'status': 'FINALIZED'})

    @staticmethod
    def search_trips(query: str) -> List[Trip]:
        """Search trips by title, province, or city"""
        return list(TripRepository.search(query))

    @staticmethod
    def calculate_trip_cost_breakdown(trip_id: int) -> Optional[Dict[str, Any]]:
        """
        محاسبه هزینه کل و breakdown به تفکیک کتگوری

        Returns:
        {
            "total_estimated_cost": Decimal,
            "breakdown_by_category": {
                "DINING": {"amount": Decimal, "percentage": float, "count": int},
                "STAY": {"amount": Decimal, "percentage": float, "count": int},
                ...
            },
            "breakdown_by_day": [
                {"day_index": 1, "date": "2026-05-01", "cost": Decimal},
                ...
            ]
        }
        """
        from django.db.models import Sum, Count

        trip = TripRepository.get_by_id(trip_id)
        if not trip:
            return None

        # جمع هزینه تمام آیتم‌ها
        items = TripItem.objects.filter(day__trip=trip)
        total = items.aggregate(Sum('estimated_cost'))[
            'estimated_cost__sum'] or Decimal('0.00')

        # Breakdown by category
        breakdown_query = items.values('category').annotate(
            amount=Sum('estimated_cost'),
            count=Count('item_id')
        )

        breakdown_by_category = {}
        for item in breakdown_query:
            category = item['category'] or 'OTHER'
            amount = item['amount'] or Decimal('0.00')
            percentage = float((amount / total * 100) if total > 0 else 0)

            breakdown_by_category[category] = {
                "amount": float(amount),
                "percentage": round(percentage, 2),
                "count": item['count']
            }

        # Breakdown by day
        day_breakdown_query = TripDay.objects.filter(
            trip=trip).prefetch_related('items')
        breakdown_by_day = []

        for day in day_breakdown_query:
            day_cost = day.items.aggregate(Sum('estimated_cost'))[
                'estimated_cost__sum'] or Decimal('0.00')
            breakdown_by_day.append({
                "day_index": day.day_index,
                "date": day.specific_date.isoformat(),
                "cost": float(day_cost)
            })

        # Update Trip model total
        trip.total_estimated_cost = total
        trip.save(update_fields=['total_estimated_cost'])

        return {
            "total_estimated_cost": float(total),
            "breakdown_by_category": breakdown_by_category,
            "breakdown_by_day": breakdown_by_day
        }


class TripDayService:
    """Business logic for TripDay operations"""

    @staticmethod
    def get_days_for_trip(trip_id: int) -> List[TripDay]:
        """Get all days for a trip"""
        return list(TripDayRepository.get_by_trip(trip_id))

    @staticmethod
    def get_day_by_id(day_id: int) -> Optional[TripDay]:
        """Get a specific day by ID"""
        return TripDayRepository.get_by_id(day_id)

    @staticmethod
    def create_day(trip_id: int, data: Dict[str, Any] = None) -> TripDay:
        """Create a new day for a trip"""
        if data is None:
            data = {}

        # Get the trip to calculate day_index and specific_date
        trip = TripRepository.get_by_id(trip_id)
        if not trip:
            raise ValueError(f"Trip with id {trip_id} not found")

        # Get existing days count to determine new day_index
        existing_days = list(TripDayRepository.get_by_trip(trip_id))
        new_day_index = len(existing_days) + 1

        # Calculate specific_date based on start_date and day_index
        from datetime import timedelta
        specific_date = trip.start_date + timedelta(days=new_day_index - 1)

        # Validate that we're not exceeding trip duration
        if new_day_index > trip.duration_days:
            raise ValueError(
                f"Cannot add more days than trip duration ({trip.duration_days})")

        day_data = {
            **data,
            'trip_id': trip_id,
            'day_index': new_day_index,
            'specific_date': specific_date
        }

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
    def get_item_by_id(item_id: int) -> Optional[TripItem]:
        """Get a specific item by ID"""
        return TripItemRepository.get_by_id(item_id)

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
        """Update a trip item with time validation"""
        from .helpers import validate_time_reschedule

        item = TripItemRepository.get_by_id(item_id)
        if not item:
            return None

        # If updating time, validate the change
        new_start_time = data.get('start_time')
        new_end_time = data.get('end_time')

        if new_start_time or new_end_time:
            validation_result = validate_time_reschedule(
                item=item,
                new_start_time=new_start_time,
                new_end_time=new_end_time
            )

            if not validation_result['valid']:
                raise ValueError(validation_result['error'])

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
            raise ValueError(
                "Cannot add dependency: would create a circular dependency")

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




import logging

# Import the mocked clients
# Note: Place these files in your project and adjust import paths as needed

logger = logging.getLogger(__name__)

# Initialize mocked clients (singleton instances)
recommendation_client = RecommendationClient(use_mocks=True)
facility_client = FacilityClient(use_mocks=True)
wiki_client = WikiClient()

class SuggestionService:

    @staticmethod
    def generate_destination_suggestions(season, budget_level, travel_style, interests):
        """
        Generate destination suggestions using mocked clients

        Args:
            season: Persian season (بهار, تابستان, پاییز, زمستان)
            budget_level: ECONOMY, MEDIUM, LUXURY, UNLIMITED
            travel_style: SOLO, COUPLE, FAMILY, FRIENDS, BUSINESS
            interests: List of Persian interest keywords

        Returns:
            List of destination suggestions with comprehensive details
        """

        # Map travel_style to Persian travel style for scoring
        travel_style_map = {
            'SOLO': 'ماجراجویی',
            'COUPLE': 'خانوادگی',
            'FAMILY': 'خانوادگی',
            'FRIENDS': 'طبیعت',
            'BUSINESS': 'شهری'
        }

        # If user has interests, use them; otherwise map from travel_style
        effective_interests = interests if interests else [travel_style_map.get(travel_style, 'تاریخی')]

        # If user has interests, use the first one as primary travel style
        if interests and len(interests) > 0:
            persian_travel_style = interests[0]
        else:
            persian_travel_style = travel_style_map.get(travel_style, 'تاریخی')

        # Step 1: Get recommended regions from RecommendationClient
        logger.info(
            f"Getting region suggestions for season={season}, budget={budget_level}, interests={effective_interests}")
        regions = recommendation_client.get_suggested_regions(
            budget_limit=budget_level,
            season=season,
            interests=effective_interests
        )

        # Take top 3 regions
        top_regions = regions[:3]

        suggestions = []

        for region in top_regions:
            try:
                province = region['province']

                # Map interests to categories for better filtering
                interest_to_categories = {
                    'تاریخی': ['HISTORICAL', 'CULTURAL'],
                    'فرهنگی': ['CULTURAL', 'HISTORICAL'],
                    'طبیعت': ['NATURAL'],
                    'خانوادگی': ['RECREATIONAL', 'NATURAL', 'DINING'],
                    'مذهبی': ['RELIGIOUS'],
                    'ماجراجویی': ['NATURAL', 'RECREATIONAL'],
                    'شهری': ['CULTURAL', 'DINING', 'STAY'],
                    'غذا': ['DINING']
                }

                # Get preferred categories based on interests
                preferred_categories = []
                if interests:
                    for interest in interests:
                        preferred_categories.extend(interest_to_categories.get(interest, []))

                # Remove duplicates while preserving order
                if preferred_categories:
                    seen = set()
                    preferred_categories = [x for x in preferred_categories if not (x in seen or seen.add(x))]

                # Step 2: Get places in this region from FacilityClient
                logger.info(f"Searching for places in {province} with categories {preferred_categories}")
                places = facility_client.search_places(
                    province=province,
                    categories=preferred_categories if preferred_categories else None,
                    budget_level=budget_level,
                    limit=5
                )

                if not places:
                    logger.warning(f"No places found for province: {province}")
                    continue

                # Step 3: Get highlights (top 2-3 attractions)
                highlights = [place['title'] for place in places[:3]]

                # Step 4: Calculate estimated cost based on budget level and places
                estimated_cost = SuggestionService.calculate_estimated_cost(budget_level, places)

                # Step 5: Determine recommended duration
                duration_days = SuggestionService.calculate_duration(len(places))

                # Step 6: Get description from WikiClient and region data
                description = region.get('description', f"استان {province} یکی از مقاصد گردشگری محبوب ایران است.")
                images = [region.get('image_url', 'https://example.com/placeholder.jpg')]

                # Try to enrich with wiki data for the first place
                if places:
                    first_place_id = places[0]['id']
                    wiki_info = wiki_client.get_place_info(first_place_id)
                    if wiki_info and wiki_info.get('description'):
                        # Combine region description with place description
                        description = f"{region.get('description', '')} {wiki_info['description'][:150]}..."
                        if wiki_info.get('images'):
                            images.extend(wiki_info['images'][:2])

                # Step 7: Generate reason based on interests and region characteristics
                reason = SuggestionService.generate_reason(
                    province=province,
                    interests=interests,
                    travel_style=persian_travel_style,
                    places=places
                )

                # Step 8: Map season back to English for response
                season_reverse_map = {
                    'بهار': 'spring',
                    'تابستان': 'summer',
                    'پاییز': 'fall',
                    'زمستان': 'winter'
                }

                best_seasons = region.get('best_seasons', [season])
                best_season_english = season_reverse_map.get(
                    best_seasons[0] if best_seasons else season,
                    'spring'
                )

                # Build comprehensive suggestion
                suggestion = {
                    'city': province,  # Using province as main city
                    'province': province,
                    'score': region['match_score'],
                    'reason': reason,
                    'highlights': highlights,
                    'best_season': best_season_english,
                    'estimated_cost': str(estimated_cost),
                    'duration_days': duration_days,
                    'description': description,
                    'images': images[:3]  # Limit to 3 images
                }

                suggestions.append(suggestion)

            except Exception as e:
                logger.error(f"Error processing region {region.get('region_name')}: {str(e)}", exc_info=True)
                continue

        return suggestions

    @staticmethod
    def calculate_estimated_cost(budget_level, places):
        """
        Calculate estimated trip cost based on budget level and places

        Args:
            budget_level: ECONOMY, MEDIUM, LUXURY, UNLIMITED
            places: List of places with entry fees

        Returns:
            Estimated cost in Rials (integer)
        """
        # Base daily costs (accommodation + food + transport per day)
        base_costs = {
            'ECONOMY': 1_500_000,  # 1.5M Rials per day
            'MEDIUM': 3_000_000,  # 3M Rials per day
            'LUXURY': 6_000_000,  # 6M Rials per day
            'UNLIMITED': 10_000_000  # 10M Rials per day
        }

        base_daily = base_costs.get(budget_level, 3_000_000)

        # Add entry fees for top attractions
        total_entry_fees = sum(place.get('entry_fee', 0) for place in places[:5])

        # Estimate for 3 days (average trip)
        total_cost = (base_daily * 3) + total_entry_fees

        return int(total_cost)

    @staticmethod
    def calculate_duration(num_places):
        """
        Calculate recommended trip duration based on number of places

        Args:
            num_places: Number of places to visit

        Returns:
            Recommended number of days (integer)
        """
        if num_places <= 3:
            return 2
        elif num_places <= 6:
            return 3
        elif num_places <= 10:
            return 4
        else:
            return 5

    @staticmethod
    def generate_reason(province, interests, travel_style, places):
        """
        Generate a personalized reason/recommendation text for the destination

        Args:
            province: Province name in Persian
            interests: User interests (list of Persian keywords)
            travel_style: User's travel style in Persian
            places: List of places in the province

        Returns:
            Reason text in Persian (string)
        """
        # Count categories in places
        categories = {}
        for place in places:
            cat = place.get('category', 'OTHER')
            categories[cat] = categories.get(cat, 0) + 1

        # Find dominant category
        dominant_category = max(categories.items(), key=lambda x: x[1])[0] if categories else None

        # Category to description mapping
        category_descriptions = {
            'HISTORICAL': 'با آثار تاریخی غنی',
            'RELIGIOUS': 'با مکان‌های مذهبی معنوی',
            'NATURAL': 'با طبیعت بکر و دیدنی',
            'CULTURAL': 'با فرهنگ غنی و بازارهای سنتی',
            'RECREATIONAL': 'با امکانات تفریحی متنوع',
            'DINING': 'با غذاهای محلی متنوع',
            'STAY': 'با امکانات اقامتی مناسب'
        }

        # Build reason
        parts = [f"استان {province}"]

        # Add category-based description
        if dominant_category and dominant_category in category_descriptions:
            parts.append(category_descriptions[dominant_category])

        # Add interest-based reason
        interest_map = {
            'تاریخی': 'برای علاقه‌مندان به تاریخ و معماری',
            'فرهنگی': 'برای علاقه‌مندان به فرهنگ و هنر',
            'طبیعت': 'برای دوستداران طبیعت و کوهنوردی',
            'خانوادگی': 'برای سفرهای خانوادگی',
            'مذهبی': 'برای زیارت و سیاحت مذهبی',
            'ماجراجویی': 'برای جویندگان ماجراجویی',
            'شهری': 'برای تجربه زندگی شهری',
            'غذا': 'برای تجربه غذاهای محلی'
        }

        if interests and len(interests) > 0:
            interest_reason = interest_map.get(interests[0], '')
            if interest_reason:
                parts.append(interest_reason)
        elif travel_style in interest_map:
            parts.append(interest_map[travel_style])

        # Add place count if significant
        if len(places) >= 5:
            parts.append(f'با بیش از {len(places)} جاذبه گردشگری')

        reason = ' '.join(parts)

        # Add quality endorsement based on average rating
        if places:
            avg_rating = sum(p.get('rating', 0) for p in places) / len(places)
            if avg_rating >= 4.7:
                reason += '. یکی از محبوب‌ترین مقاصد گردشگری ایران'
            elif avg_rating >= 4.5:
                reason += '. مقصدی عالی برای سفر'

        return reason
