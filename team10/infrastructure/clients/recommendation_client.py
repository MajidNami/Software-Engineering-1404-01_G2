import random
from typing import List

from ..ports.recommendation_service_port import RecommendationServicePort
from ..models.recommended_place import RecommendedPlace
from ...domain.enums.season import Season


class MockRecommendationClient(RecommendationServicePort):
    """Mock implementation of RecommendationServicePort for development."""

    # Mock place pools per region (region_id -> list of place_ids)
    MOCK_PLACES = {
        # Tehran
        "1": ["برج_میلاد", "کاخ_گلستان", "پل_طبیعت", "بازار_بزرگ_تهران", "مجموعه_سعدآباد"],
        # Isfahan
        "2": ["میدان_نقش_جهان", "سی_و_سه_پل", "مسجد_شیخ_لطف_الله", "کاخ_عالی_قاپو", "کلیسای_وانک"],
        # Shiraz
        "3": ["حافظیه", "تخت_جمشید", "ارگ_کریمخان", "باغ_ارم", "نارنجستان_قوام"],
        # Mashhad
        "4": ["حرم_امام_رضا", "باغ_نادری", "کوه_سنگی", "پارک_ملت", "موزه_آستان_قدس"],
        # Tabriz
        "5": ["بازار_تبریز", "مسجد_کبود", "ائل_گلی", "ارگ_علیشاه", "قلعه_بابک"],
        # Yazd
        "6": ["مسجد_جامع_یزد", "باغ_دولت_آباد", "برج_خاموشان", "زندان_اسکندر", "آتشکده_یزد"],
        # Kerman
        "7": ["باغ_شاهزاده_ماهان", "گنبد_جبلیه", "بازار_سرچشمه", "مجموعه_گنجعلیخان", "کلوت_شهداد"],
        # Rasht
        "8": ["بازار_رشت", "موزه_میراث_روستایی", "تالاب_انزلی", "قلعه_رودخان", "پارک_جنگلی_سراوان"],
        # Kish
        "9": ["پارک_مرجانی", "شهر_زیرزمینی_کاریز", "کشتی_یونانی", "ساحل_مرجان", "اسکله_تفریحی"],
        # Qeshm
        "10": ["جنگل_حرا", "دره_ستارگان", "غار_نمکدان", "تنگه_چاهکوه", "ساحل_مرجانی"],
    }

    # Default places for unknown regions
    DEFAULT_PLACES = ["مکان_پیشنهادی_۱", "مکان_پیشنهادی_۲", "مکان_پیشنهادی_۳",
                      "مکان_پیشنهادی_۴", "مکان_پیشنهادی_۵"]

    def get_recommendations(
        self,
        user_id: str,
        region_id: str,
        destination: str,
        season: Season
    ) -> List[RecommendedPlace]:
        """Return place recommendations.

        This is still a *mock* recommender, but the scores are made **deterministic**
        per (user_id, region_id, destination, season) so that UI tests and manual
        QA are reproducible.
        """

        places = self.MOCK_PLACES.get(region_id, self.DEFAULT_PLACES)

        # Deterministic pseudo-random generator for stable results
        seed = hash((user_id, region_id, destination, season.value)) & 0xFFFFFFFF
        rng = random.Random(seed)

        recommendations = []
        for place_id in places:
            # Keep scores in a realistic band; later can be replaced by real ML.
            score = round(rng.uniform(0.70, 0.95), 2)
            recommendations.append(RecommendedPlace(place_id=place_id, score=score))

        # Sort by score descending
        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations
