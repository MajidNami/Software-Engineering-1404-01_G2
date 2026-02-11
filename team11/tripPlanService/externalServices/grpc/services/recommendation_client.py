
import grpc
from typing import List, Dict

from externalServices.grpc.client.Clients import Clients


class RecommendationClient:
    """
    gRPC Client برای ارتباط با Recommendation Service
    """


    def rank_places(
        self,
        places: List[Dict],
        user_interests: List[str]
    ) -> List[Dict]:
        client=Clients.get_recom_client()
        """
        رتبه‌بندی مکان‌ها بر اساس interests کاربر

        gRPC Method: RankPlaces(RankRequest) → RankResponse
        """
        # TODO: پیاده‌سازی با استفاده از recom.proto

        # فعلاً همون لیست اصلی رو برمی‌گردونه
        return places