
from typing import Optional, Dict

from team11.tripPlanService.externalServices.grpc.client.Clients import Clients


class WikiClient:
    """
    gRPC Client برای ارتباط با Wiki Service
    """
    def get_place_info(self, place_id: str) -> Optional[Dict]:
        client=Clients.get_wiki_client()
        """
        دریافت اطلاعات تاریخی/فرهنگی یک مکان

        gRPC Method: GetPlaceWiki(WikiRequest) → WikiResponse
        """
        # TODO: پیاده‌سازی با استفاده از wiki.proto
        return {
            'title': 'آرامگاه حافظ',
            'description': 'مزار خواجه شمس‌الدین محمد حافظ شیرازی...',
            'history': 'بنا شده در سال...',
            'images': ['url1', 'url2']
        }