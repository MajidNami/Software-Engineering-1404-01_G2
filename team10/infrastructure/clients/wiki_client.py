from typing import Dict

from ..ports.wiki_service_port import WikiServicePort


class MockWikiClient(WikiServicePort):
    """Mock implementation of WikiServicePort for development."""

    # Mock destination descriptions
    MOCK_DESCRIPTIONS: Dict[str, str] = {
        "tehran": "تهران پایتخت و بزرگترین شهر ایران است. این شهر مرکز سیاسی، اقتصادی و فرهنگی کشور محسوب می‌شود.",
        "isfahan": "اصفهان یکی از شهرهای تاریخی ایران است که به خاطر معماری اسلامی و میدان نقش جهان شهرت جهانی دارد.",
        "shiraz": "شیراز شهر شاعران و گل‌های رنگارنگ است. این شهر زادگاه حافظ و سعدی است.",
        "mashhad": "مشهد دومین شهر پرجمعیت ایران و مهمترین مرکز زیارتی کشور است.",
        "tabriz": "تبریز یکی از قدیمی‌ترین شهرهای ایران و مرکز استان آذربایجان شرقی است.",
        "yazd": "یزد شهر بادگیرها و قنات‌هاست و به عنوان میراث جهانی یونسکو ثبت شده است.",
        "kerman": "کرمان شهری تاریخی با آثار باستانی متعدد و صنایع دستی منحصربفرد است.",
        "rasht": "رشت مرکز استان گیلان و پایتخت غذایی ایران است.",
        "kish": "جزیره کیش یکی از مقاصد گردشگری محبوب ایران در خلیج فارس است.",
        "qeshm": "قشم بزرگترین جزیره خلیج فارس با جاذبه‌های طبیعی منحصربفرد است.",
    }

    # Name aliases for lookup
    NAME_ALIASES = {
        "tehran": "tehran", "تهران": "tehran",
        "isfahan": "isfahan", "esfahan": "isfahan", "اصفهان": "isfahan",
        "shiraz": "shiraz", "شیراز": "shiraz",
        "mashhad": "mashhad", "mashad": "mashhad", "مشهد": "mashhad",
        "tabriz": "tabriz", "تبریز": "tabriz",
        "yazd": "yazd", "یزد": "yazd",
        "kerman": "kerman", "کرمان": "kerman",
        "rasht": "rasht", "رشت": "rasht",
        "kish": "kish", "کیش": "kish",
        "qeshm": "qeshm", "قشم": "qeshm",
    }

    def get_destination_basic_info(self, destination_name: str) -> str:
        """Get basic description about a destination.
        
        Returns an empty string if the destination is not found.
        """
        normalized = destination_name.strip().lower()
        
        # Direct lookup
        key = self.NAME_ALIASES.get(normalized)
        if key and key in self.MOCK_DESCRIPTIONS:
            return self.MOCK_DESCRIPTIONS[key]
        
        # Partial match
        for alias, key in self.NAME_ALIASES.items():
            if alias in normalized or normalized in alias:
                return self.MOCK_DESCRIPTIONS[key]
        
        # Return empty string for unknown destinations
        return ""
