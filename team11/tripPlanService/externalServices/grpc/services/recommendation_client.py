"""
Recommendation Service Client - Fully Mocked with Comprehensive Iranian Data
"""
import logging
from typing import List, Dict, Optional
import random

logger = logging.getLogger(__name__)


class RecommendationClient:
    """
    Fully mocked client for recommendation service
    Provides intelligent scoring and region suggestions based on Iranian provinces
    """

    def __init__(self, base_url: str = 'http://localhost:8000/api', use_mocks: bool = True):
        self.base_url = base_url.rstrip('/')
        self.use_mocks = use_mocks
        logger.info("RecommendationClient initialized in FULL MOCK mode")

        # Initialize mock data
        self._initialize_mock_data()

    def _initialize_mock_data(self):
        """Initialize comprehensive mock data for Iranian provinces"""

        # Region data for all Iranian provinces
        self.regions = [
            # Popular tourist provinces
            {
                'region_id': 'reg_isfahan',
                'region_name': 'استان اصفهان',
                'province': 'اصفهان',
                'description': 'نصف جهان با میراث صفوی غنی',
                'image_url': 'https://example.com/isfahan.jpg',
                'best_seasons': ['بهار', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM', 'LUXURY'],
                'base_score': 95
            },
            {
                'region_id': 'reg_fars',
                'region_name': 'استان فارس',
                'province': 'فارس',
                'description': 'تخت جمشید و میراث هخامنشی',
                'image_url': 'https://example.com/fars.jpg',
                'best_seasons': ['بهار', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM', 'LUXURY'],
                'base_score': 93
            },
            {
                'region_id': 'reg_yazd',
                'region_name': 'استان یزد',
                'province': 'یزد',
                'description': 'شهر بادگیرها و معماری خشتی',
                'image_url': 'https://example.com/yazd.jpg',
                'best_seasons': ['بهار', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 88
            },
            {
                'region_id': 'reg_gilan',
                'region_name': 'استان گیلان',
                'province': 'گیلان',
                'description': 'جنگل‌های سبز و طبیعت بکر شمال',
                'image_url': 'https://example.com/gilan.jpg',
                'best_seasons': ['بهار', 'تابستان', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM', 'LUXURY'],
                'base_score': 90
            },
            {
                'region_id': 'reg_mazandaran',
                'region_name': 'استان مازندران',
                'province': 'مازندران',
                'description': 'ساحل دریای خزر و جنگل‌های هیرکانی',
                'image_url': 'https://example.com/mazandaran.jpg',
                'best_seasons': ['بهار', 'تابستان', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM', 'LUXURY'],
                'base_score': 89
            },
            {
                'region_id': 'reg_tehran',
                'region_name': 'استان تهران',
                'province': 'تهران',
                'description': 'پایتخت پرجنب‌وجوش ایران',
                'image_url': 'https://example.com/tehran.jpg',
                'best_seasons': ['بهار', 'پاییز'],
                'budget_suitability': ['MEDIUM', 'LUXURY'],
                'base_score': 85
            },
            {
                'region_id': 'reg_khorasan_razavi',
                'region_name': 'استان خراسان رضوی',
                'province': 'خراسان رضوی',
                'description': 'شهر مقدس مشهد و حرم امام رضا',
                'image_url': 'https://example.com/mashhad.jpg',
                'best_seasons': ['بهار', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM', 'LUXURY'],
                'base_score': 94  # Increased from 92 for religious significance
            },
            {
                'region_id': 'reg_kerman',
                'region_name': 'استان کرمان',
                'province': 'کرمان',
                'description': 'کویر لوت و طبیعت بی‌نظیر',
                'image_url': 'https://example.com/kerman.jpg',
                'best_seasons': ['بهار', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 87
            },
            {
                'region_id': 'reg_hormozgan',
                'region_name': 'استان هرمزگان',
                'province': 'هرمزگان',
                'description': 'جزایر خلیج فارس و قشم',
                'image_url': 'https://example.com/hormozgan.jpg',
                'best_seasons': ['پاییز', 'زمستان', 'بهار'],
                'budget_suitability': ['ECONOMY', 'MEDIUM', 'LUXURY'],
                'base_score': 86
            },
            {
                'region_id': 'reg_khuzestan',
                'region_name': 'استان خوزستان',
                'province': 'خوزستان',
                'description': 'تمدن عیلام و شوش باستانی',
                'image_url': 'https://example.com/khuzestan.jpg',
                'best_seasons': ['پاییز', 'زمستان', 'بهار'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 82
            },
            {
                'region_id': 'reg_azarbaijan_sharqi',
                'region_name': 'استان آذربایجان شرقی',
                'province': 'آذربایجان شرقی',
                'description': 'تبریز و بازار تاریخی یونسکو',
                'image_url': 'https://example.com/tabriz.jpg',
                'best_seasons': ['بهار', 'تابستان', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 84
            },
            {
                'region_id': 'reg_hamedan',
                'region_name': 'استان همدان',
                'province': 'همدان',
                'description': 'غار علیصدر و آرامگاه بوعلی',
                'image_url': 'https://example.com/hamedan.jpg',
                'best_seasons': ['بهار', 'تابستان', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 85
            },
            {
                'region_id': 'reg_lorestan',
                'region_name': 'استان لرستان',
                'province': 'لرستان',
                'description': 'آبشارهای زیبا و طبیعت کوهستانی',
                'image_url': 'https://example.com/lorestan.jpg',
                'best_seasons': ['بهار', 'تابستان'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 81
            },
            {
                'region_id': 'reg_bushehr',
                'region_name': 'استان بوشهر',
                'province': 'بوشهر',
                'description': 'معماری خلیج فارس و ساحل جنوب',
                'image_url': 'https://example.com/bushehr.jpg',
                'best_seasons': ['پاییز', 'زمستان', 'بهار'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 78
            },
            {
                'region_id': 'reg_sistan',
                'region_name': 'استان سیستان و بلوچستان',
                'province': 'سیستان و بلوچستان',
                'description': 'فرهنگ بلوچی و طبیعت منحصر به فرد',
                'image_url': 'https://example.com/sistan.jpg',
                'best_seasons': ['پاییز', 'زمستان', 'بهار'],
                'budget_suitability': ['ECONOMY'],
                'base_score': 75
            },
            {
                'region_id': 'reg_zanjan',
                'region_name': 'استان زنجان',
                'province': 'زنجان',
                'description': 'غار کتله‌خور و گنبد سلطانیه',
                'image_url': 'https://example.com/zanjan.jpg',
                'best_seasons': ['بهار', 'تابستان', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 83
            },
            {
                'region_id': 'reg_semnan',
                'region_name': 'استان سمنان',
                'province': 'سمنان',
                'description': 'کویر مرنجاب و کاروانسرا',
                'image_url': 'https://example.com/semnan.jpg',
                'best_seasons': ['پاییز', 'زمستان', 'بهار'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 80
            },
            {
                'region_id': 'reg_qazvin',
                'region_name': 'استان قزوین',
                'province': 'قزوین',
                'description': 'قلعه الموت و تاریخ حسن صباح',
                'image_url': 'https://example.com/qazvin.jpg',
                'best_seasons': ['بهار', 'تابستان', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 82
            },
            {
                'region_id': 'reg_qom',
                'region_name': 'استان قم',
                'province': 'قم',
                'description': 'شهر مذهبی و حرم حضرت معصومه',
                'image_url': 'https://example.com/qom.jpg',
                'best_seasons': ['بهار', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 79
            },
            {
                'region_id': 'reg_markazi',
                'region_name': 'استان مرکزی',
                'province': 'مرکزی',
                'description': 'تپه نوش جان و آثار باستانی',
                'image_url': 'https://example.com/markazi.jpg',
                'best_seasons': ['بهار', 'پاییز'],
                'budget_suitability': ['ECONOMY'],
                'base_score': 72
            },
            {
                'region_id': 'reg_ilam',
                'region_name': 'استان ایلام',
                'province': 'ایلام',
                'description': 'آبشارها و طبیعت زاگرس',
                'image_url': 'https://example.com/ilam.jpg',
                'best_seasons': ['بهار', 'تابستان'],
                'budget_suitability': ['ECONOMY'],
                'base_score': 76
            },
            {
                'region_id': 'reg_kohgiluyeh',
                'region_name': 'استان کهگیلویه و بویراحمد',
                'province': 'کهگیلویه و بویراحمد',
                'description': 'دریاچه و آبشار مارگون',
                'image_url': 'https://example.com/kohgiluyeh.jpg',
                'best_seasons': ['بهار', 'تابستان'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 84
            },
            {
                'region_id': 'reg_chaharmahal',
                'region_name': 'استان چهارمحال و بختیاری',
                'province': 'چهارمحال و بختیاری',
                'description': 'دشت‌های سبز و کوهستان بختیاری',
                'image_url': 'https://example.com/chaharmahal.jpg',
                'best_seasons': ['بهار', 'تابستان'],
                'budget_suitability': ['ECONOMY'],
                'base_score': 77
            },
            {
                'region_id': 'reg_kurdistan',
                'region_name': 'استان کردستان',
                'province': 'کردستان',
                'description': 'دریاچه زریوار و قوری قلعه',
                'image_url': 'https://example.com/kurdistan.jpg',
                'best_seasons': ['بهار', 'تابستان'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 83
            },
            {
                'region_id': 'reg_kermanshah',
                'region_name': 'استان کرمانشاه',
                'province': 'کرمانشاه',
                'description': 'طاق بستان و بیستون یونسکو',
                'image_url': 'https://example.com/Kermanshah.jpg',
                'best_seasons': ['بهار', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 86
            },
            {
                'region_id': 'reg_ardabil',
                'region_name': 'استان اردبیل',
                'province': 'اردبیل',
                'description': 'کوه سبلان و چشمه‌های آبگرم',
                'image_url': 'https://example.com/ardabil.jpg',
                'best_seasons': ['بهار', 'تابستان', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 85
            },
            {
                'region_id': 'reg_azarbaijan_gharbi',
                'region_name': 'استان آذربایجان غربی',
                'province': 'آذربایجان غربی',
                'description': 'کلیساهای ارامنه و تخت سلیمان',
                'image_url': 'https://example.com/west-azarbaijan.jpg',
                'best_seasons': ['بهار', 'تابستان'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 82
            },
            {
                'region_id': 'reg_golestan',
                'region_name': 'استان گلستان',
                'province': 'گلستان',
                'description': 'جنگل‌های هیرکانی و پارک ملی',
                'image_url': 'https://example.com/golestan.jpg',
                'best_seasons': ['بهار', 'تابستان', 'پاییز'],
                'budget_suitability': ['ECONOMY', 'MEDIUM'],
                'base_score': 81
            },
            {
                'region_id': 'reg_alborz',
                'region_name': 'استان البرز',
                'province': 'البرز',
                'description': 'پیست اسکی دیزین و کوهستان البرز',
                'image_url': 'https://example.com/alborz.jpg',
                'best_seasons': ['زمستان', 'بهار', 'پاییز'],
                'budget_suitability': ['MEDIUM', 'LUXURY'],
                'base_score': 84
            },
            {
                'region_id': 'reg_khorasan_north',
                'region_name': 'استان خراسان شمالی',
                'province': 'خراسان شمالی',
                'description': 'آبشار زیارت و طبیعت بکر',
                'image_url': 'https://example.com/north-khorasan.jpg',
                'best_seasons': ['بهار', 'تابستان'],
                'budget_suitability': ['ECONOMY'],
                'base_score': 74
            },
            {
                'region_id': 'reg_khorasan_south',
                'region_name': 'استان خراسان جنوبی',
                'province': 'خراسان جنوبی',
                'description': 'قلعه فورگ و باغ اکبریه',
                'image_url': 'https://example.com/south-khorasan.jpg',
                'best_seasons': ['بهار', 'پاییز'],
                'budget_suitability': ['ECONOMY'],
                'base_score': 73
            },
        ]

        # Travel style preferences for scoring
        self.travel_style_preferences = {
            'تاریخی': {
                'preferred_categories': ['HISTORICAL', 'CULTURAL', 'RELIGIOUS'],
                'weight': 1.5
            },
            'فرهنگی': {
                'preferred_categories': ['CULTURAL', 'HISTORICAL'],
                'weight': 1.4
            },
            'طبیعت': {
                'preferred_categories': ['NATURAL', 'RECREATIONAL'],
                'weight': 1.6
            },
            'خانوادگی': {
                'preferred_categories': ['RECREATIONAL', 'NATURAL', 'DINING'],
                'weight': 1.3
            },
            'ماجراجویی': {
                'preferred_categories': ['NATURAL', 'RECREATIONAL'],
                'weight': 1.5
            },
            'مذهبی': {
                'preferred_categories': ['RELIGIOUS'],
                'weight': 1.8
            },
            'شهری': {
                'preferred_categories': ['CULTURAL', 'DINING', 'STAY'],
                'weight': 1.2
            }
        }

    def get_scored_places(
            self,
            candidate_place_ids: List[str],
            travel_style: str,
            budget_level: str,
            trip_duration: int
    ) -> Dict[str, float]:
        """
        API 1: Get intelligent scores for a list of places

        Args:
            candidate_place_ids: List of place IDs to score
            travel_style: User's travel style (تاریخی, طبیعت, etc.)
            budget_level: ECONOMY, MEDIUM, LUXURY, UNLIMITED
            trip_duration: Number of days

        Returns:
            Dictionary mapping place_id to score (0-100)
        """
        logger.info(f"Scoring {len(candidate_place_ids)} places for {travel_style} style, {budget_level} budget")

        scores = {}

        # Get travel style preferences
        style_prefs = self.travel_style_preferences.get(travel_style, {
            'preferred_categories': [],
            'weight': 1.0
        })

        for place_id in candidate_place_ids:
            # Base score
            base_score = random.uniform(60, 85)

            # Add some variation based on place_id for consistency
            id_hash = sum(ord(c) for c in place_id)
            base_score += (id_hash % 10)

            # Apply travel style weight
            score = base_score * style_prefs['weight']

            # Budget adjustment
            if budget_level == 'ECONOMY':
                score *= 0.95  # Slight preference for budget options
            elif budget_level == 'LUXURY':
                score *= 1.05  # Slight boost for luxury

            # Duration adjustment (longer trips = more diverse recommendations)
            if trip_duration > 5:
                score *= 1.02

            # Normalize to 0-100
            score = min(100, max(0, score))

            scores[place_id] = round(score, 2)

        return scores

    def get_suggested_regions(
            self,
            budget_limit: str,
            season: str,
            interests: List[str] = None
    ) -> List[Dict]:
        """
        API 2: Suggest regions based on budget, season, and interests

        Args:
            budget_limit: ECONOMY, MEDIUM, LUXURY, UNLIMITED
            season: بهار, تابستان, پاییز, زمستان
            interests: List of Persian interest keywords (optional)

        Returns:
            List of regions with match scores
        """
        logger.info(f"Suggesting regions for {season} season with {budget_limit} budget and interests: {interests}")

        # Interest to province mapping for variety (ordered by relevance)
        interest_province_boost = {
            'تاریخی': ['اصفهان', 'فارس', 'کرمانشاه', 'یزد', 'خوزستان'],
            'فرهنگی': ['یزد', 'فارس', 'آذربایجان شرقی', 'اصفهان', 'تهران'],
            'طبیعت': ['گیلان', 'مازندران', 'کردستان', 'کهگیلویه و بویراحمد', 'لرستان'],
            'خانوادگی': ['مازندران', 'گیلان', 'البرز', 'فارس', 'کرمان'],
            'مذهبی': ['خراسان رضوی', 'قم', 'فارس', 'کرمانشاه', 'همدان'],
            'ماجراجویی': ['اردبیل', 'البرز', 'لرستان', 'کهگیلویه و بویراحمد', 'کرمان'],
            'شهری': ['تهران', 'آذربایجان شرقی', 'فارس', 'اصفهان', 'خراسان رضوی'],
            'غذا': ['گیلان', 'آذربایجان شرقی', 'مازندران', 'اصفهان', 'فارس']
        }

        suggested_regions = []

        for region in self.regions:
            # Check budget suitability
            if budget_limit not in region['budget_suitability'] and budget_limit != 'UNLIMITED':
                continue

            # Start with a lower base to make interest boosts more impactful
            match_score = region['base_score'] * 0.7  # Reduce base score impact

            # Season bonus
            if season in region['best_seasons']:
                match_score += 15

            # Budget exact match bonus
            if budget_limit in region['budget_suitability']:
                match_score += 5

            # Interest-based boost (MUCH higher weight for matching interests)
            if interests:
                has_match = False
                for interest in interests:
                    if interest in interest_province_boost:
                        preferred_provinces = interest_province_boost[interest]
                        if region['province'] in preferred_provinces:
                            # Very high boost for interest matches
                            position = preferred_provinces.index(region['province'])
                            interest_boost = 40 - (position * 4)  # 40, 36, 32, 28, 24
                            match_score += interest_boost
                            has_match = True

                # Strong penalty for non-matching provinces when interests are specified
                if not has_match:
                    match_score -= 25

            suggested_regions.append({
                'region_id': region['region_id'],
                'region_name': region['region_name'],
                'province': region['province'],
                'description': region['description'],
                'match_score': min(100, max(0, int(match_score))),  # Clamp between 0-100
                'image_url': region['image_url'],
                'best_seasons': region.get('best_seasons', [season])
            })

        # Sort by match score with some randomization for variety
        suggested_regions.sort(key=lambda x: x['match_score'], reverse=True)

        # Return top 10
        return suggested_regions[:10]

    def get_places_in_region(
            self,
            region_id: str,
            travel_style: str,
            budget_level: str,
            trip_duration: int
    ) -> List[Dict]:
        """
        API 3: Suggest places in a specific region

        Args:
            region_id: Region identifier
            travel_style: User's travel style
            budget_level: Budget level
            trip_duration: Number of days

        Returns:
            List of {place_id, score} for places in the region
        """
        logger.info(f"Getting places in region {region_id} for {travel_style} style")

        # Find the region
        region = None
        for r in self.regions:
            if r['region_id'] == region_id:
                region = r
                break

        if not region:
            logger.warning(f"Region {region_id} not found")
            return []

        # Generate mock place IDs for this region
        # In real implementation, this would query the facility service
        province = region['province']

        # Create place IDs based on province
        place_ids = [
            f'place_{region_id}_001',
            f'place_{region_id}_002',
            f'place_{region_id}_003',
            f'place_{region_id}_004',
            f'place_{region_id}_005',
        ]

        # Score the places
        scores = self.get_scored_places(
            place_ids,
            travel_style,
            budget_level,
            trip_duration
        )

        # Convert to list format
        scored_places = [
            {'place_id': pid, 'score': score}
            for pid, score in scores.items()
        ]

        # Sort by score
        scored_places.sort(key=lambda x: x['score'], reverse=True)

        return scored_places

    def rank_places(
            self,
            places: List[Dict],
            user_interests: List[str]
    ) -> List[Dict]:
        """
        Legacy method for backward compatibility
        Ranks places based on user interests

        Args:
            places: List of place dictionaries
            user_interests: List of interest keywords

        Returns:
            Sorted list of places
        """
        return self._mock_ranking(places, user_interests)

    def _mock_ranking(
            self,
            places: List[Dict],
            user_interests: List[str]
    ) -> List[Dict]:
        """Enhanced mock ranking based on category match and other factors"""

        # Interest to category mapping
        interest_mapping = {
            'تاریخی': ['HISTORICAL', 'RELIGIOUS', 'CULTURAL'],
            'فرهنگی': ['CULTURAL', 'HISTORICAL'],
            'طبیعت': ['NATURAL', 'RECREATIONAL'],
            'خانوادگی': ['RECREATIONAL', 'NATURAL', 'DINING'],
            'مذهبی': ['RELIGIOUS'],
            'غذا': ['DINING'],
            'ماجراجویی': ['NATURAL', 'RECREATIONAL'],
            'شهری': ['CULTURAL', 'DINING', 'STAY']
        }

        # Get relevant categories
        relevant_categories = []
        for interest in user_interests:
            relevant_categories.extend(interest_mapping.get(interest, []))

        # Score places
        scored_places = []
        for place in places:
            score = 0

            # Category match score
            if place.get('category') in relevant_categories:
                score += 15

            # Rating score
            score += place.get('rating', 0) * 3

            # Review count bonus (popular places)
            review_count = place.get('review_count', 0)
            if review_count > 10000:
                score += 8
            elif review_count > 5000:
                score += 5
            elif review_count > 1000:
                score += 3

            # Price tier preference
            price_tier = place.get('price_tier', 'MODERATE')
            if price_tier == 'FREE':
                score += 5
            elif price_tier == 'BUDGET':
                score += 3

            # Province diversity bonus (for varied experiences)
            province = place.get('province', '')
            if province:
                score += 1

            scored_places.append((score, place))

        # Sort by score descending
        scored_places.sort(reverse=True, key=lambda x: x[0])

        return [place for score, place in scored_places]

    def get_region_by_province(self, province: str) -> Optional[Dict]:
        """
        Helper method to get region info by province name

        Args:
            province: Province name (e.g., 'اصفهان')

        Returns:
            Region dictionary or None
        """
        for region in self.regions:
            if region['province'] == province:
                return region
        return None


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    client = RecommendationClient(use_mocks=True)

    # Test 1: Get suggested regions for spring with economy budget
    print("\n=== Test 1: Suggested regions for spring (economy) ===")
    regions = client.get_suggested_regions(budget_limit='ECONOMY', season='بهار')
    for region in regions[:5]:
        print(f"- {region['region_name']} (Score: {region['match_score']})")
        print(f"  {region['description']}")

    # Test 2: Score some places
    print("\n=== Test 2: Score places for historical travel ===")
    place_ids = ['place_001', 'place_002', 'place_003', 'place_004']
    scores = client.get_scored_places(
        place_ids,
        travel_style='تاریخی',
        budget_level='MEDIUM',
        trip_duration=3
    )
    for pid, score in scores.items():
        print(f"- {pid}: {score}")

    # Test 3: Get places in Isfahan region
    print("\n=== Test 3: Places in Isfahan region ===")
    places = client.get_places_in_region(
        region_id='reg_isfahan',
        travel_style='تاریخی',
        budget_level='MEDIUM',
        trip_duration=3
    )
    for place in places:
        print(f"- {place['place_id']}: {place['score']}")

    # Test 4: Test legacy ranking
    print("\n=== Test 4: Legacy ranking test ===")
    mock_places = [
        {'id': '1', 'category': 'HISTORICAL', 'rating': 4.8, 'review_count': 12000, 'price_tier': 'FREE', 'province': 'اصفهان'},
        {'id': '2', 'category': 'NATURAL', 'rating': 4.5, 'review_count': 3000, 'price_tier': 'BUDGET', 'province': 'گیلان'},
        {'id': '3', 'category': 'DINING', 'rating': 4.2, 'review_count': 800, 'price_tier': 'MODERATE', 'province': 'تهران'},
    ]
    ranked = client.rank_places(mock_places, user_interests=['تاریخی'])
    for i, place in enumerate(ranked, 1):
        print(f"{i}. Category: {place['category']}, Rating: {place['rating']}, Province: {place['province']}")

    print("\n=== Summary ===")
    print(f"Total regions available: {len(client.regions)}")
    print(f"Travel styles supported: {len(client.travel_style_preferences)}")