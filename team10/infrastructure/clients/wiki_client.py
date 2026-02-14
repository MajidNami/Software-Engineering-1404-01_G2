from typing import Dict

from ..ports.wiki_service_port import WikiServicePort


class MockWikiClient(WikiServicePort):
    """Mock implementation of WikiServicePort for development."""

    # Mock destination descriptions
    MOCK_DESCRIPTIONS: Dict[str, str] = {
        "tehran": (
            "تهران پایتخت و بزرگترین شهر ایران است و نقش پررنگی در سیاست، اقتصاد و فرهنگ کشور دارد. "
            "از جاذبه‌های شاخص آن می‌توان به کاخ گلستان، برج میلاد، بازار بزرگ و موزه‌ها و پارک‌های متعدد اشاره کرد."
        ),
        "isfahan": (
            "اصفهان شهری تاریخی با معماری برجسته ایرانی-اسلامی است. "
            "میدان نقش جهان، سی‌وسه‌پل و بناهای صفوی از مهم‌ترین دیدنی‌های این شهر به شمار می‌آیند."
        ),
        "shiraz": (
            "شیراز شهر شعر و ادب و باغ‌های ایرانی است و با نام حافظ و سعدی گره خورده است. "
            "نزدیکی به تخت جمشید و وجود باغ‌ها و بناهای تاریخی، آن را به مقصد گردشگری مهمی تبدیل کرده است."
        ),
        "mashhad": (
            "مشهد دومین شهر پرجمعیت ایران و مهم‌ترین مقصد زیارتی کشور است. "
            "حرم امام رضا (ع) و مجموعه‌های فرهنگی-موزه‌ای اطراف آن از شاخص‌ترین نقاط شهر هستند."
        ),
        "tabriz": (
            "تبریز از شهرهای تاریخی ایران در شمال‌غرب کشور است. "
            "بازار تاریخی تبریز (ثبت جهانی) و مجموعه ائل‌گلی از شناخته‌شده‌ترین جاذبه‌های آن هستند."
        ),
        "yazd": (
            "یزد با بافت تاریخی خشتی، بادگیرها و قنات‌ها شناخته می‌شود و در فهرست میراث جهانی یونسکو ثبت شده است. "
            "دیدنی‌های مهم آن شامل مسجد جامع، باغ دولت‌آباد و مجموعه‌های تاریخی در بافت قدیم است."
        ),
        "kerman": (
            "کرمان شهری تاریخی در جنوب‌شرق ایران است و به‌خاطر بازارها، کاروانسراها و نزدیکی به جاذبه‌های کویری شهرت دارد. "
            "باغ شاهزاده ماهان و مجموعه گنجعلی‌خان از نقاط پرطرفدار آن هستند."
        ),
        "rasht": (
            "رشت مرکز استان گیلان است و به طبیعت سرسبز و فرهنگ غذایی محلی مشهور است. "
            "بازار سنتی، میدان شهرداری و دسترسی به جاذبه‌های اطراف مانند قلعه رودخان و تالاب انزلی از مزیت‌های آن است."
        ),
        "kish": (
            "جزیره کیش یکی از مقاصد گردشگری و خرید در خلیج فارس است. "
            "سواحل، اسکله تفریحی و جاذبه‌هایی مانند کشتی یونانی و شهر زیرزمینی کاریز از دیدنی‌های آن هستند."
        ),
        "qeshm": (
            "قشم بزرگ‌ترین جزیره ایران است و با ژئوپارک و جاذبه‌های طبیعی شناخته می‌شود. "
            "جنگل‌های حرا، دره ستارگان و تنگه چاهکوه از مشهورترین نقاط گردشگری قشم هستند."
        ),
        "ahvaz": "اهواز مرکز استان خوزستان است و رودخانه کارون از میان شهر عبور می‌کند.",
        "bandarabbas": "بندرعباس بندری مهم در جنوب ایران و مرکز استان هرمزگان است.",
        "hamedan": "همدان از قدیمی‌ترین شهرهای ایران است و جاذبه‌هایی مانند غار علیصدر و تپه هگمتانه دارد.",
        "qom": "قم شهری مذهبی و مرکز حوزه‌های علمیه است و حرم حضرت معصومه (س) در آن قرار دارد.",
        "kashan": "کاشان شهری تاریخی با خانه‌های سنتی و باغ فین است.",
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

        "ahvaz": "ahvaz", "اهواز": "ahvaz",
        "bandarabbas": "bandarabbas", "بندرعباس": "bandarabbas",
        "hamedan": "hamedan", "همدان": "hamedan",
        "qom": "qom", "قم": "qom",
        "kashan": "kashan", "کاشان": "kashan",
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
