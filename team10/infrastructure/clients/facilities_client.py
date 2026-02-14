import math
from typing import List, Optional, Dict
from datetime import datetime

from ..ports.facilities_service_port import FacilitiesServicePort
from ..models.region import Region
from ..models.search_criteria import SearchCriteria
from ..models.facility_cost_estimate import FacilityCostEstimate
from ..models.travel_info import TravelInfo, TransportMode
from ...domain.models.facility import Facility


class MockFacilitiesClient(FacilitiesServicePort):
    """Mock implementation of FacilitiesServicePort for development.
    
    This mock provides:
    - Hotels and restaurants for each region
    - Facility details for recommended places (attractions)
    - Travel info between facilities
    
    Note: The actual attractions/places of interest come from the Recommender service.
    This service provides the facility details (coordinates, hours, etc.) for those places.
    """

    # Primary names are Persian; used for database (destination_name) and display
    MOCK_REGIONS = [
        Region(id="1", name="تهران"),
        Region(id="2", name="اصفهان"),
        Region(id="3", name="شیراز"),
        Region(id="4", name="مشهد"),
        Region(id="5", name="تبریز"),
        Region(id="6", name="یزد"),
        Region(id="7", name="کرمان"),
        Region(id="8", name="رشت"),
        Region(id="9", name="کیش"),
        Region(id="10", name="قشم"),
        Region(id="11", name="اهواز"),
        Region(id="12", name="بندرعباس"),
        Region(id="13", name="همدان"),
        Region(id="14", name="قم"),
        Region(id="15", name="کاشان"),
    ]

    # Mapping of Persian names and alternative spellings to region IDs
    NAME_ALIASES = {
        # Tehran
        "tehran": "1", "تهران": "1",
        # Isfahan
        "isfahan": "2", "esfahan": "2", "اصفهان": "2",
        # Shiraz
        "shiraz": "3", "شیراز": "3",
        # Mashhad
        "mashhad": "4", "mashad": "4", "مشهد": "4",
        # Tabriz
        "tabriz": "5", "تبریز": "5",
        # Yazd
        "yazd": "6", "یزد": "6",
        # Kerman
        "kerman": "7", "کرمان": "7",
        # Rasht
        "rasht": "8", "رشت": "8",
        # Kish
        "kish": "9", "کیش": "9",
        # Qeshm
        "qeshm": "10", "قشم": "10",
        # Ahvaz
        "ahvaz": "11", "اهواز": "11",
        # Bandar Abbas
        "bandar abbas": "12", "bandarabbas": "12", "بندرعباس": "12",
        # Hamadan
        "hamadan": "13", "hamedan": "13", "همدان": "13",
        # Qom
        "qom": "14", "قم": "14",
        # Kashan
        "kashan": "15", "کاشان": "15",
    }

    # Mock facilities data - Hotels and Restaurants organized by region
    # Costs are in Rials (Iranian currency).
    # NOTE: Hotel/restaurant pricing changes frequently; values here are *reasonable defaults*
    # for UI/demo flows and can be tuned later.
    MOCK_FACILITIES: Dict[str, List[Facility]] = {
        # Tehran (region_id: "1")
        "1": [
            # Hotels
            Facility(id=1001, name="هتل استقلال", facility_type="HOTEL", latitude=35.7796, longitude=51.4108,
                     cost=15000000, region_id="1", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.5, description="هتل پنج ستاره استقلال تهران"),
            Facility(id=1002, name="هتل آزادی", facility_type="HOTEL", latitude=35.7219, longitude=51.3347,
                     cost=12000000, region_id="1", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.3, description="هتل پنج ستاره آزادی"),
            Facility(id=1003, name="هتل ایبیس", facility_type="HOTEL", latitude=35.7010, longitude=51.4014,
                     cost=5000000, region_id="1", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=3.8, description="هتل سه ستاره ایبیس"),
            Facility(id=1004, name="هتل ایران", facility_type="HOTEL", latitude=35.6892, longitude=51.3890,
                     cost=2500000, region_id="1", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.0, description="هتل دو ستاره ایران"),
            # Restaurants
            Facility(id=1101, name="رستوران دیزی سرا", facility_type="RESTAURANT", latitude=35.7156, longitude=51.4194,
                     cost=800000, region_id="1", visit_duration_minutes=90, opening_hour=11, closing_hour=23,
                     tags=["food", "traditional"], rating=4.2, description="رستوران سنتی دیزی سرا"),
            Facility(id=1102, name="رستوران نایب", facility_type="RESTAURANT", latitude=35.7589, longitude=51.4103,
                     cost=1200000, region_id="1", visit_duration_minutes=90, opening_hour=12, closing_hour=24,
                     tags=["food", "kebab"], rating=4.5, description="رستوران نایب - کباب"),
            Facility(id=1103, name="فست فود سامان", facility_type="RESTAURANT", latitude=35.7012, longitude=51.4050,
                     cost=400000, region_id="1", visit_duration_minutes=45, opening_hour=10, closing_hour=23,
                     tags=["food", "fast_food"], rating=3.5, description="فست فود سامان"),
        ],
        # Isfahan (region_id: "2")
        "2": [
            # Hotels
            Facility(id=2001, name="هتل عباسی", facility_type="HOTEL", latitude=32.6539, longitude=51.6660,
                     cost=18000000, region_id="2", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury", "historic"], rating=4.8, description="هتل تاریخی عباسی - قدیمی‌ترین هتل ایران"),
            Facility(id=2002, name="هتل کوثر", facility_type="HOTEL", latitude=32.6446, longitude=51.6553,
                     cost=8000000, region_id="2", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=4.0, description="هتل کوثر اصفهان"),
            Facility(id=2003, name="هتل ستاره", facility_type="HOTEL", latitude=32.6500, longitude=51.6700,
                     cost=3000000, region_id="2", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.2, description="هتل ستاره اصفهان"),
            # Restaurants
            Facility(id=2101, name="رستوران شهرزاد", facility_type="RESTAURANT", latitude=32.6550, longitude=51.6600,
                     cost=900000, region_id="2", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "traditional"], rating=4.4, description="رستوران سنتی شهرزاد"),
            Facility(id=2102, name="سفره خانه سنتی", facility_type="RESTAURANT", latitude=32.6570, longitude=51.6680,
                     cost=600000, region_id="2", visit_duration_minutes=90, opening_hour=11, closing_hour=22,
                     tags=["food", "traditional"], rating=4.0, description="سفره خانه سنتی اصفهان"),
        ],
        # Shiraz (region_id: "3")
        "3": [
            # Hotels
            Facility(id=3001, name="هتل چمران", facility_type="HOTEL", latitude=29.6314, longitude=52.5279,
                     cost=10000000, region_id="3", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.3, description="هتل بزرگ چمران شیراز"),
            Facility(id=3002, name="هتل پارس", facility_type="HOTEL", latitude=29.6200, longitude=52.5350,
                     cost=6000000, region_id="3", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=3.9, description="هتل پارس شیراز"),
            Facility(id=3003, name="هتل ارم", facility_type="HOTEL", latitude=29.6150, longitude=52.5400,
                     cost=2000000, region_id="3", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.0, description="هتل ارم شیراز"),
            # Restaurants
            Facility(id=3101, name="رستوران شاطر عباس", facility_type="RESTAURANT", latitude=29.6250, longitude=52.5300,
                     cost=700000, region_id="3", visit_duration_minutes=90, opening_hour=11, closing_hour=23,
                     tags=["food", "traditional"], rating=4.3, description="رستوران شاطر عباس"),
            Facility(id=3102, name="رستوران هفت خوان", facility_type="RESTAURANT", latitude=29.6180, longitude=52.5380,
                     cost=1000000, region_id="3", visit_duration_minutes=90, opening_hour=12, closing_hour=24,
                     tags=["food", "traditional"], rating=4.5, description="رستوران هفت خوان"),
        ],

        # Mashhad (region_id: "4")
        "4": [
            # Hotels (approx. coordinates near city center)
            Facility(id=4001, name="هتل درویشی", facility_type="HOTEL", latitude=36.2890, longitude=59.6130,
                     cost=16000000, region_id="4", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.6, description="هتل پنج ستاره درویشی مشهد"),
            Facility(id=4002, name="هتل قصر طلایی", facility_type="HOTEL", latitude=36.2895, longitude=59.6115,
                     cost=14000000, region_id="4", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.5, description="هتل پنج ستاره قصر طلایی مشهد"),
            Facility(id=4003, name="هتل الماس ۲", facility_type="HOTEL", latitude=36.2885, longitude=59.6122,
                     cost=9000000, region_id="4", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=4.2, description="هتل الماس ۲ مشهد"),
            # Restaurants
            Facility(id=4101, name="رستوران پسران کریم", facility_type="RESTAURANT", latitude=36.2870, longitude=59.6105,
                     cost=1200000, region_id="4", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "kebab"], rating=4.3, description="رستوران معروف پسران کریم"),
            Facility(id=4102, name="رستوران معین درباری", facility_type="RESTAURANT", latitude=36.2867, longitude=59.6110,
                     cost=1100000, region_id="4", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "traditional"], rating=4.2, description="رستوران معین درباری مشهد"),
        ],

        # Tabriz (region_id: "5")
        "5": [
            # Hotels (approx.)
            Facility(id=5001, name="هتل پارس ائل‌گلی", facility_type="HOTEL", latitude=38.0230, longitude=46.3600,
                     cost=12000000, region_id="5", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.2, description="هتل پارس ائل‌گلی تبریز"),
            Facility(id=5002, name="هتل لاله پارک", facility_type="HOTEL", latitude=38.0700, longitude=46.3600,
                     cost=13000000, region_id="5", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.3, description="هتل لاله پارک تبریز"),
            Facility(id=5003, name="هتل شهریار", facility_type="HOTEL", latitude=38.0750, longitude=46.2800,
                     cost=8000000, region_id="5", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=4.0, description="هتل شهریار تبریز"),
            # Restaurants
            Facility(id=5101, name="رستوران برکه", facility_type="RESTAURANT", latitude=38.0750, longitude=46.2900,
                     cost=900000, region_id="5", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "traditional"], rating=4.1, description="رستوران سنتی برکه تبریز"),
            Facility(id=5102, name="رستوران حاج علی", facility_type="RESTAURANT", latitude=38.0705, longitude=46.2960,
                     cost=850000, region_id="5", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "kebab"], rating=4.0, description="رستوران حاج علی تبریز"),
        ],

        # Yazd (region_id: "6")
        "6": [
            # Hotels
            Facility(id=6001, name="هتل داد", facility_type="HOTEL", latitude=31.88578, longitude=54.36591,
                     cost=9000000, region_id="6", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["historic", "moderate"], rating=4.4, description="هتل تاریخی داد یزد"),
            Facility(id=6002, name="هتل صفائیه", facility_type="HOTEL", latitude=31.8800, longitude=54.3560,
                     cost=12000000, region_id="6", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.5, description="هتل صفائیه یزد"),
            Facility(id=6003, name="هتل ملک‌التجار", facility_type="HOTEL", latitude=31.8970, longitude=54.3660,
                     cost=8000000, region_id="6", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["historic"], rating=4.1, description="هتل سنتی ملک‌التجار"),
            # Restaurants
            Facility(id=6101, name="رستوران هتل داد", facility_type="RESTAURANT", latitude=31.88578, longitude=54.36591,
                     cost=900000, region_id="6", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "traditional"], rating=4.2, description="رستوران مجموعه هتل داد"),
            Facility(id=6102, name="رستوران ترمه و ترنج", facility_type="RESTAURANT", latitude=31.8972, longitude=54.3672,
                     cost=800000, region_id="6", visit_duration_minutes=90, opening_hour=12, closing_hour=22,
                     tags=["food", "traditional"], rating=4.0, description="رستوران سنتی در بافت تاریخی"),
        ],

        # Kerman (region_id: "7")
        "7": [
            # Hotels (approx.)
            Facility(id=7001, name="هتل پارس کرمان", facility_type="HOTEL", latitude=30.2839, longitude=57.0834,
                     cost=9000000, region_id="7", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=4.0, description="هتل پارس کرمان"),
            Facility(id=7002, name="هتل جهانگردی", facility_type="HOTEL", latitude=30.2900, longitude=57.0800,
                     cost=6000000, region_id="7", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.7, description="هتل جهانگردی کرمان"),
            Facility(id=7003, name="هتل اخوان", facility_type="HOTEL", latitude=30.2875, longitude=57.0780,
                     cost=5000000, region_id="7", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.6, description="هتل اخوان کرمان"),
            # Restaurants
            Facility(id=7101, name="رستوران عمارت وکیل", facility_type="RESTAURANT", latitude=30.2880, longitude=57.0790,
                     cost=900000, region_id="7", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "traditional"], rating=4.1, description="رستوران سنتی در بافت تاریخی"),
            Facility(id=7102, name="کافه رستوران گواوا", facility_type="RESTAURANT", latitude=30.2865, longitude=57.0820,
                     cost=700000, region_id="7", visit_duration_minutes=60, opening_hour=10, closing_hour=23,
                     tags=["food", "cafe"], rating=4.0, description="کافه رستوران مدرن"),
        ],

        # Rasht (region_id: "8")
        "8": [
            # Hotels (approx.)
            Facility(id=8001, name="هتل کادوس بزرگ", facility_type="HOTEL", latitude=37.2808, longitude=49.5831,
                     cost=8000000, region_id="8", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=4.0, description="هتل کادوس بزرگ رشت"),
            Facility(id=8002, name="هتل شبستان", facility_type="HOTEL", latitude=37.2750, longitude=49.5950,
                     cost=5000000, region_id="8", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.7, description="هتل شبستان رشت"),
            Facility(id=8003, name="هتل پامچال", facility_type="HOTEL", latitude=37.2790, longitude=49.5900,
                     cost=4200000, region_id="8", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.5, description="هتل پامچال رشت"),
            # Restaurants
            Facility(id=8101, name="رستوران محرم", facility_type="RESTAURANT", latitude=37.2793, longitude=49.5846,
                     cost=900000, region_id="8", visit_duration_minutes=90, opening_hour=11, closing_hour=23,
                     tags=["food", "local"], rating=4.2, description="غذاهای محلی گیلانی"),
            Facility(id=8102, name="رستوران گیلانه", facility_type="RESTAURANT", latitude=37.2810, longitude=49.5820,
                     cost=950000, region_id="8", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "local"], rating=4.1, description="رستوران با منوی گیلانی"),
        ],

        # Kish (region_id: "9")
        "9": [
            # Hotels
            Facility(id=9001, name="هتل داریوش", facility_type="HOTEL", latitude=26.53504, longitude=54.02770,
                     cost=16000000, region_id="9", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.4, description="هتل پنج ستاره داریوش کیش"),
            Facility(id=9002, name="هتل ترنج", facility_type="HOTEL", latitude=26.5600, longitude=53.9500,
                     cost=18000000, region_id="9", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["luxury"], rating=4.5, description="هتل دریایی ترنج کیش"),
            Facility(id=9003, name="هتل شایان", facility_type="HOTEL", latitude=26.5580, longitude=54.0200,
                     cost=11000000, region_id="9", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=4.0, description="هتل شایان کیش"),
            # Restaurants
            Facility(id=9101, name="رستوران میرمهنا", facility_type="RESTAURANT", latitude=26.5578, longitude=54.0194,
                     cost=1400000, region_id="9", visit_duration_minutes=90, opening_hour=12, closing_hour=24,
                     tags=["food", "seafood"], rating=4.2, description="رستوران دریایی میرمهنا"),
            Facility(id=9102, name="رستوران کوه نور", facility_type="RESTAURANT", latitude=26.5550, longitude=54.0220,
                     cost=1300000, region_id="9", visit_duration_minutes=90, opening_hour=12, closing_hour=24,
                     tags=["food", "traditional"], rating=4.1, description="رستوران کوه نور کیش"),
        ],

        # Qeshm (region_id: "10")
        "10": [
            # Hotels (approx.)
            Facility(id=10001, name="هتل آتامان", facility_type="HOTEL", latitude=26.9560, longitude=56.2690,
                     cost=8000000, region_id="10", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["moderate"], rating=4.0, description="هتل آتامان قشم"),
            Facility(id=10002, name="هتل ارم", facility_type="HOTEL", latitude=26.9620, longitude=56.2695,
                     cost=6500000, region_id="10", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.7, description="هتل ارم قشم"),
            Facility(id=10003, name="هتل دیپلمات", facility_type="HOTEL", latitude=26.9550, longitude=56.2680,
                     cost=5500000, region_id="10", visit_duration_minutes=0, opening_hour=0, closing_hour=24,
                     tags=["economy"], rating=3.5, description="هتل دیپلمات قشم"),
            # Restaurants
            Facility(id=10101, name="رستوران خاله", facility_type="RESTAURANT", latitude=26.9565, longitude=56.2700,
                     cost=1200000, region_id="10", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "seafood"], rating=4.1, description="رستوران دریایی خاله"),
            Facility(id=10102, name="رستوران نعیم", facility_type="RESTAURANT", latitude=26.9575, longitude=56.2685,
                     cost=1100000, region_id="10", visit_duration_minutes=90, opening_hour=12, closing_hour=23,
                     tags=["food", "seafood"], rating=4.0, description="غذاهای دریایی و محلی"),
        ],
    }

    # Facility details for places recommended by the Recommender service
    # These are attractions/points of interest - the Recommender gives us place_ids,
    # and this mapping provides the full facility details
    PLACE_FACILITIES: Dict[str, Dict[str, Facility]] = {
        "1": {  # Tehran
            "برج_میلاد": Facility(id=1201, name="برج میلاد", facility_type="ATTRACTION", latitude=35.7448, longitude=51.3753,
                     cost=500000, region_id="1", visit_duration_minutes=120, opening_hour=9, closing_hour=22,
                     tags=["modern", "sightseeing"], rating=4.3, description="برج میلاد - نماد مدرن تهران"),
            "کاخ_گلستان": Facility(id=1202, name="کاخ گلستان", facility_type="ATTRACTION", latitude=35.6775, longitude=51.4181,
                     cost=300000, region_id="1", visit_duration_minutes=150, opening_hour=9, closing_hour=17,
                     tags=["history", "culture"], rating=4.7, description="کاخ گلستان - میراث جهانی یونسکو"),
            "پل_طبیعت": Facility(id=1203, name="پل طبیعت", facility_type="ATTRACTION", latitude=35.7635, longitude=51.4053,
                     cost=0, region_id="1", visit_duration_minutes=60, opening_hour=6, closing_hour=24,
                     tags=["nature", "modern"], rating=4.4, description="پل طبیعت - پل عابر پیاده"),
            "بازار_بزرگ_تهران": Facility(id=1204, name="بازار بزرگ تهران", facility_type="ATTRACTION", latitude=35.6762, longitude=51.4258,
                     cost=0, region_id="1", visit_duration_minutes=180, opening_hour=8, closing_hour=18,
                     tags=["shopping", "history"], rating=4.1, description="بازار بزرگ تهران"),
            "مجموعه_سعدآباد": Facility(id=1205, name="مجموعه سعدآباد", facility_type="ATTRACTION", latitude=35.8186, longitude=51.4089,
                     cost=400000, region_id="1", visit_duration_minutes=180, opening_hour=9, closing_hour=17,
                     tags=["history", "culture", "nature"], rating=4.5, description="مجموعه کاخ‌های سعدآباد"),
        },
        "2": {  # Isfahan
            "میدان_نقش_جهان": Facility(id=2201, name="میدان نقش جهان", facility_type="ATTRACTION", latitude=32.6575, longitude=51.6774,
                     cost=0, region_id="2", visit_duration_minutes=120, opening_hour=6, closing_hour=22,
                     tags=["history", "culture", "shopping"], rating=4.9, description="میدان نقش جهان - میراث جهانی"),
            "سی_و_سه_پل": Facility(id=2202, name="سی و سه پل", facility_type="ATTRACTION", latitude=32.6431, longitude=51.6689,
                     cost=0, region_id="2", visit_duration_minutes=60, opening_hour=0, closing_hour=24,
                     tags=["history", "nature"], rating=4.6, description="پل سی و سه چشمه"),
            "مسجد_شیخ_لطف_الله": Facility(id=2203, name="مسجد شیخ لطف الله", facility_type="ATTRACTION", latitude=32.6574, longitude=51.6780,
                     cost=200000, region_id="2", visit_duration_minutes=60, opening_hour=9, closing_hour=17,
                     tags=["history", "culture", "religion"], rating=4.8, description="مسجد شیخ لطف‌الله"),
            "کاخ_عالی_قاپو": Facility(id=2204, name="کاخ عالی قاپو", facility_type="ATTRACTION", latitude=32.6572, longitude=51.6771,
                     cost=250000, region_id="2", visit_duration_minutes=90, opening_hour=9, closing_hour=18,
                     tags=["history", "culture"], rating=4.5, description="کاخ عالی قاپو"),
            "کلیسای_وانک": Facility(id=2205, name="کلیسای وانک", facility_type="ATTRACTION", latitude=32.634922, longitude=51.655792,
                     cost=150000, region_id="2", visit_duration_minutes=90, opening_hour=9, closing_hour=17,
                     tags=["history", "culture", "religion"], rating=4.4, description="کلیسای وانک جلفا"),
        },
        "3": {  # Shiraz
            "حافظیه": Facility(id=3201, name="حافظیه", facility_type="ATTRACTION", latitude=29.6207, longitude=52.5549,
                     cost=150000, region_id="3", visit_duration_minutes=90, opening_hour=8, closing_hour=22,
                     tags=["history", "culture", "nature"], rating=4.8, description="آرامگاه حافظ"),
            "تخت_جمشید": Facility(id=3202, name="تخت جمشید", facility_type="ATTRACTION", latitude=29.9352, longitude=52.8908,
                     cost=500000, region_id="3", visit_duration_minutes=240, opening_hour=8, closing_hour=17,
                     tags=["history", "culture"], rating=4.9, description="تخت جمشید - میراث جهانی"),
            "ارگ_کریمخان": Facility(id=3203, name="ارگ کریمخان", facility_type="ATTRACTION", latitude=29.6109, longitude=52.5389,
                     cost=200000, region_id="3", visit_duration_minutes=90, opening_hour=8, closing_hour=18,
                     tags=["history", "culture"], rating=4.4, description="ارگ کریمخان زند"),
            "باغ_ارم": Facility(id=3204, name="باغ ارم", facility_type="ATTRACTION", latitude=29.6356, longitude=52.5203,
                     cost=100000, region_id="3", visit_duration_minutes=90, opening_hour=8, closing_hour=20,
                     tags=["nature", "history"], rating=4.5, description="باغ ارم - میراث جهانی"),
            "نارنجستان_قوام": Facility(id=3205, name="نارنجستان قوام", facility_type="ATTRACTION", latitude=29.6125, longitude=52.5458,
                     cost=150000, region_id="3", visit_duration_minutes=60, opening_hour=8, closing_hour=18,
                     tags=["history", "culture", "nature"], rating=4.3, description="خانه قوام - نارنجستان"),
        },

        "4": {  # Mashhad
            "حرم_امام_رضا": Facility(id=4201, name="حرم امام رضا", facility_type="ATTRACTION", latitude=36.28723, longitude=59.61586,
                     cost=0, region_id="4", visit_duration_minutes=180, opening_hour=0, closing_hour=24,
                     tags=["religion", "culture"], rating=4.9, description="حرم امام رضا (ع) - مهم‌ترین مرکز زیارتی ایران"),
            "باغ_نادری": Facility(id=4202, name="باغ نادری (آرامگاه نادرشاه)", facility_type="ATTRACTION", latitude=36.29479, longitude=59.61061,
                     cost=200000, region_id="4", visit_duration_minutes=90, opening_hour=8, closing_hour=19,
                     tags=["history", "museum"], rating=4.4, description="مجموعه باغ نادری و آرامگاه نادرشاه"),
            "کوه_سنگی": Facility(id=4203, name="پارک کوه‌سنگی", facility_type="ATTRACTION", latitude=36.28278, longitude=59.56750,
                     cost=0, region_id="4", visit_duration_minutes=120, opening_hour=0, closing_hour=24,
                     tags=["park", "nature"], rating=4.5, description="پارک کوه‌سنگی مشهد"),
            "پارک_ملت": Facility(id=4204, name="پارک ملت", facility_type="ATTRACTION", latitude=36.32111, longitude=59.53778,
                     cost=0, region_id="4", visit_duration_minutes=120, opening_hour=0, closing_hour=24,
                     tags=["park", "nature"], rating=4.4, description="پارک ملت مشهد"),
            "موزه_آستان_قدس": Facility(id=4205, name="موزه آستان قدس رضوی", facility_type="ATTRACTION", latitude=36.28780, longitude=59.61630,
                     cost=150000, region_id="4", visit_duration_minutes=120, opening_hour=8, closing_hour=17,
                     tags=["museum", "culture"], rating=4.3, description="موزه‌های آستان قدس رضوی"),
        },

        "5": {  # Tabriz
            "بازار_تبریز": Facility(id=5201, name="بازار تاریخی تبریز", facility_type="ATTRACTION", latitude=38.08139, longitude=46.29306,
                     cost=0, region_id="5", visit_duration_minutes=150, opening_hour=9, closing_hour=17,
                     tags=["shopping", "history"], rating=4.6, description="بازار تاریخی تبریز (ثبت جهانی یونسکو)"),
            "مسجد_کبود": Facility(id=5202, name="مسجد کبود تبریز", facility_type="ATTRACTION", latitude=38.07361, longitude=46.30083,
                     cost=100000, region_id="5", visit_duration_minutes=60, opening_hour=9, closing_hour=17,
                     tags=["history", "culture", "religion"], rating=4.4, description="مسجد کبود (فیروزه اسلام)"),
            "ائل_گلی": Facility(id=5203, name="ائل‌گلی (شاه‌گلی)", facility_type="ATTRACTION", latitude=38.02540, longitude=46.36411,
                     cost=0, region_id="5", visit_duration_minutes=120, opening_hour=0, closing_hour=24,
                     tags=["park", "nature"], rating=4.5, description="پارک ائل‌گلی تبریز"),
            "ارگ_علیشاه": Facility(id=5204, name="ارگ علی‌شاه", facility_type="ATTRACTION", latitude=38.06660, longitude=46.29050,
                     cost=0, region_id="5", visit_duration_minutes=60, opening_hour=9, closing_hour=17,
                     tags=["history", "culture"], rating=4.1, description="بقایای ارگ علی‌شاه تبریز"),
            "قلعه_بابک": Facility(id=5205, name="قلعه بابک", facility_type="ATTRACTION", latitude=38.84200, longitude=47.02800,
                     cost=0, region_id="5", visit_duration_minutes=240, opening_hour=8, closing_hour=18,
                     tags=["history", "hiking"], rating=4.6, description="قلعه بابک (نزدیک کلیبر)"),
        },

        "6": {  # Yazd
            "مسجد_جامع_یزد": Facility(id=6201, name="مسجد جامع یزد", facility_type="ATTRACTION", latitude=31.89700, longitude=54.36770,
                     cost=0, region_id="6", visit_duration_minutes=60, opening_hour=8, closing_hour=20,
                     tags=["history", "religion", "architecture"], rating=4.6, description="مسجد جامع یزد (کاشی‌کاری و مناره‌های بلند)"),
            "باغ_دولت_آباد": Facility(id=6202, name="باغ دولت‌آباد", facility_type="ATTRACTION", latitude=31.88890, longitude=54.36690,
                     cost=150000, region_id="6", visit_duration_minutes=90, opening_hour=8, closing_hour=20,
                     tags=["nature", "history"], rating=4.6, description="باغ دولت‌آباد و بادگیر معروف"),
            "برج_خاموشان": Facility(id=6203, name="دخمه زرتشتیان (برج خاموشان)", facility_type="ATTRACTION", latitude=31.95000, longitude=54.34600,
                     cost=100000, region_id="6", visit_duration_minutes=90, opening_hour=8, closing_hour=18,
                     tags=["history", "culture"], rating=4.2, description="برج خاموشان (دخمه زرتشتیان)"),
            "زندان_اسکندر": Facility(id=6204, name="زندان اسکندر", facility_type="ATTRACTION", latitude=31.89780, longitude=54.36720,
                     cost=80000, region_id="6", visit_duration_minutes=60, opening_hour=8, closing_hour=20,
                     tags=["history", "culture"], rating=4.1, description="مدرسه ضیائیه (معروف به زندان اسکندر)"),
            "آتشکده_یزد": Facility(id=6205, name="آتشکده یزد", facility_type="ATTRACTION", latitude=31.89950, longitude=54.36890,
                     cost=120000, region_id="6", visit_duration_minutes=60, opening_hour=8, closing_hour=20,
                     tags=["religion", "culture"], rating=4.3, description="آتشکده یزد (آتش ورهرام)"),
        },

        "7": {  # Kerman
            "باغ_شاهزاده_ماهان": Facility(id=7201, name="باغ شاهزاده ماهان", facility_type="ATTRACTION", latitude=30.02295, longitude=57.28114,
                     cost=200000, region_id="7", visit_duration_minutes=120, opening_hour=8, closing_hour=18,
                     tags=["nature", "history"], rating=4.7, description="باغ شاهزاده ماهان"),
            "گنبد_جبلیه": Facility(id=7202, name="گنبد جبلیه", facility_type="ATTRACTION", latitude=30.29233, longitude=57.11681,
                     cost=0, region_id="7", visit_duration_minutes=45, opening_hour=8, closing_hour=18,
                     tags=["history", "architecture"], rating=4.1, description="گنبد سنگی جبلیه"),
            "بازار_سرچشمه": Facility(id=7203, name="بازار تاریخی کرمان (سرچشمه)", facility_type="ATTRACTION", latitude=30.28850, longitude=57.07850,
                     cost=0, region_id="7", visit_duration_minutes=120, opening_hour=9, closing_hour=18,
                     tags=["shopping", "history"], rating=4.2, description="بازار وکیل/گنجعلیخان و راسته‌های تاریخی کرمان"),
            "مجموعه_گنجعلیخان": Facility(id=7204, name="مجموعه گنجعلی‌خان", facility_type="ATTRACTION", latitude=30.29056, longitude=57.07833,
                     cost=150000, region_id="7", visit_duration_minutes=120, opening_hour=9, closing_hour=17,
                     tags=["history", "museum"], rating=4.5, description="مجموعه گنجعلی‌خان (حمام، بازار و ...)"),
            "کلوت_شهداد": Facility(id=7205, name="کلوت‌های شهداد (کویر لوت)", facility_type="ATTRACTION", latitude=30.41670, longitude=57.68330,
                     cost=0, region_id="7", visit_duration_minutes=240, opening_hour=0, closing_hour=24,
                     tags=["nature", "desert"], rating=4.6, description="کلوت‌های شهداد در حاشیه کویر لوت"),
        },

        "8": {  # Rasht
            "بازار_رشت": Facility(id=8201, name="بازار رشت", facility_type="ATTRACTION", latitude=37.28083, longitude=49.58306,
                     cost=0, region_id="8", visit_duration_minutes=120, opening_hour=8, closing_hour=18,
                     tags=["shopping", "local"], rating=4.3, description="بازار سنتی رشت"),
            "موزه_میراث_روستایی": Facility(id=8202, name="موزه میراث روستایی گیلان", facility_type="ATTRACTION", latitude=37.22700, longitude=49.70200,
                     cost=200000, region_id="8", visit_duration_minutes=150, opening_hour=9, closing_hour=17,
                     tags=["museum", "culture"], rating=4.5, description="موزه میراث روستایی گیلان (سراوان)"),
            "تالاب_انزلی": Facility(id=8203, name="تالاب انزلی", facility_type="ATTRACTION", latitude=37.46930, longitude=49.45730,
                     cost=0, region_id="8", visit_duration_minutes=180, opening_hour=0, closing_hour=24,
                     tags=["nature", "wildlife"], rating=4.4, description="تالاب انزلی"),
            "قلعه_رودخان": Facility(id=8204, name="قلعه رودخان", facility_type="ATTRACTION", latitude=37.06444, longitude=49.24000,
                     cost=150000, region_id="8", visit_duration_minutes=240, opening_hour=8, closing_hour=18,
                     tags=["history", "hiking"], rating=4.7, description="قلعه رودخان (فومن)"),
            "پارک_جنگلی_سراوان": Facility(id=8205, name="پارک جنگلی سراوان", facility_type="ATTRACTION", latitude=37.22700, longitude=49.70200,
                     cost=0, region_id="8", visit_duration_minutes=180, opening_hour=0, closing_hour=24,
                     tags=["nature", "park"], rating=4.3, description="پارک جنگلی سراوان"),
        },

        "9": {  # Kish
            "پارک_مرجانی": Facility(id=9201, name="پارک ساحلی مرجان", facility_type="ATTRACTION", latitude=26.54600, longitude=54.07000,
                     cost=0, region_id="9", visit_duration_minutes=120, opening_hour=0, closing_hour=24,
                     tags=["beach", "nature"], rating=4.5, description="پارک ساحلی مرجان"),
            "شهر_زیرزمینی_کاریز": Facility(id=9202, name="شهر زیرزمینی کاریز", facility_type="ATTRACTION", latitude=26.55667, longitude=53.96889,
                     cost=300000, region_id="9", visit_duration_minutes=90, opening_hour=9, closing_hour=18,
                     tags=["history", "underground"], rating=4.2, description="قنات/شهر زیرزمینی کاریز کیش"),
            "کشتی_یونانی": Facility(id=9203, name="کشتی یونانی", facility_type="ATTRACTION", latitude=26.52611, longitude=53.90806,
                     cost=0, region_id="9", visit_duration_minutes=60, opening_hour=0, closing_hour=24,
                     tags=["beach", "sightseeing"], rating=4.3, description="کشتی یونانی (غروب‌های معروف کیش)"),
            "ساحل_مرجان": Facility(id=9204, name="ساحل مرجان", facility_type="ATTRACTION", latitude=26.54600, longitude=54.07000,
                     cost=0, region_id="9", visit_duration_minutes=120, opening_hour=0, closing_hour=24,
                     tags=["beach"], rating=4.5, description="ساحل مرجان"),
            "اسکله_تفریحی": Facility(id=9205, name="اسکله تفریحی کیش", facility_type="ATTRACTION", latitude=26.55778, longitude=54.01944,
                     cost=0, region_id="9", visit_duration_minutes=120, opening_hour=0, closing_hour=24,
                     tags=["beach", "recreation"], rating=4.4, description="اسکله تفریحی کیش"),
        },

        "10": {  # Qeshm
            "جنگل_حرا": Facility(id=10201, name="جنگل حرا", facility_type="ATTRACTION", latitude=26.70817, longitude=55.91692,
                     cost=0, region_id="10", visit_duration_minutes=180, opening_hour=0, closing_hour=24,
                     tags=["nature", "mangrove"], rating=4.6, description="جنگل‌های حرا (مانگرو) قشم"),
            "دره_ستارگان": Facility(id=10202, name="دره ستارگان", facility_type="ATTRACTION", latitude=26.84280, longitude=55.86780,
                     cost=250000, region_id="10", visit_duration_minutes=120, opening_hour=8, closing_hour=20,
                     tags=["nature", "geopark"], rating=4.6, description="دره ستارگان (ژئوپارک قشم)"),
            "غار_نمکدان": Facility(id=10203, name="غار نمکدان", facility_type="ATTRACTION", latitude=26.61750, longitude=55.51667,
                     cost=0, region_id="10", visit_duration_minutes=150, opening_hour=0, closing_hour=24,
                     tags=["nature", "cave"], rating=4.5, description="غار نمکدان (از طولانی‌ترین غارهای نمکی جهان)"),
            "تنگه_چاهکوه": Facility(id=10204, name="تنگه چاهکوه", facility_type="ATTRACTION", latitude=26.68419, longitude=55.53779,
                     cost=200000, region_id="10", visit_duration_minutes=150, opening_hour=0, closing_hour=24,
                     tags=["nature", "canyon"], rating=4.6, description="تنگه چاهکوه"),
            # The previous mock used "ساحل_مرجانی"; keep it as a stable key.
            "ساحل_مرجانی": Facility(id=10205, name="ساحل/اسکله قشم (نمونه)", facility_type="ATTRACTION", latitude=26.69528, longitude=55.61833,
                     cost=0, region_id="10", visit_duration_minutes=120, opening_hour=0, closing_hour=24,
                     tags=["beach"], rating=4.2, description="نمونه ساحلی در قشم (برای ماک)"),
        },
    }

    def __init__(self):
        """Initialize the mock client with facility lookup cache."""
        self._facility_cache: Dict[int, Facility] = {}
        # Cache hotels and restaurants
        for region_id, facilities in self.MOCK_FACILITIES.items():
            for facility in facilities:
                self._facility_cache[facility.id] = facility
        # Cache attractions from place facilities
        for region_id, places in self.PLACE_FACILITIES.items():
            for place_id, facility in places.items():
                self._facility_cache[facility.id] = facility

    def search_region(self, query: str) -> Optional[Region]:
        normalized = query.strip().lower()

        # Exact match on aliases
        if normalized in self.NAME_ALIASES:
            region_id = self.NAME_ALIASES[normalized]
            return next(r for r in self.MOCK_REGIONS if r.id == region_id)

        # Partial match on aliases
        for alias, region_id in self.NAME_ALIASES.items():
            if alias in normalized or normalized in alias:
                return next(r for r in self.MOCK_REGIONS if r.id == region_id)

        # No match found
        return None

    def find_facilities_in_area(self, criteria: SearchCriteria) -> List[Facility]:
        """Find facilities matching search criteria."""
        results = []
        for facility in self._facility_cache.values():
            # Check distance from criteria center
            distance = self._calculate_distance(
                criteria.latitude, criteria.longitude,
                facility.latitude, facility.longitude
            )
            if distance <= criteria.radius:
                if criteria.facility_type is None or facility.facility_type == criteria.facility_type:
                    results.append(facility)
        return results

    def get_cost_estimate(
        self,
        facility_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> FacilityCostEstimate:
        facility = self._facility_cache.get(facility_id)
        if facility:
            days = (end_date - start_date).days or 1
            estimated_cost = facility.cost * days
        else:
            estimated_cost = 0.0
        
        return FacilityCostEstimate(
            facility_id=facility_id,
            estimated_cost=estimated_cost,
            period_start=start_date,
            period_end=end_date
        )

    def get_facility_by_id(self, facility_id: int) -> Optional[Facility]:
        """Get a facility by its ID."""
        return self._facility_cache.get(facility_id)

    def get_facility_by_place_id(self, place_id: str, region_id: str) -> Optional[Facility]:
        """Get facility details for a place from the recommendation service."""
        places = self.PLACE_FACILITIES.get(region_id, {})
        return places.get(place_id)

    def get_hotels_in_region(self, region_id: str) -> List[Facility]:
        """Get all hotels in a region."""
        facilities = self.MOCK_FACILITIES.get(region_id, [])
        return [f for f in facilities if f.facility_type == "HOTEL"]

    def get_restaurants_in_region(self, region_id: str) -> List[Facility]:
        """Get all restaurants in a region."""
        facilities = self.MOCK_FACILITIES.get(region_id, [])
        return [f for f in facilities if f.facility_type == "RESTAURANT"]

    def get_travel_info(self, from_facility_id: int, to_facility_id: int) -> TravelInfo:
        """Get travel information between two facilities.
        
        Returns distance, time, transport mode, and estimated cost.
        """
        from_facility = self._facility_cache.get(from_facility_id)
        to_facility = self._facility_cache.get(to_facility_id)
        
        if not from_facility or not to_facility:
            # Default fallback if facilities not found
            return TravelInfo(
                from_facility_id=from_facility_id,
                to_facility_id=to_facility_id,
                distance_km=5.0,
                duration_minutes=15,
                transport_mode=TransportMode.TAXI,
                estimated_cost=200000  # Default cost
            )
        
        # Calculate distance
        distance_km = self._calculate_distance(
            from_facility.latitude, from_facility.longitude,
            to_facility.latitude, to_facility.longitude
        )
        
        # Determine transport mode, duration, and cost based on distance
        if distance_km <= 1.0:
            transport_mode = TransportMode.WALKING
            duration_minutes = int(distance_km * 12)  # ~5 km/h walking
            estimated_cost = 0  # Walking is free
        elif distance_km <= 3.0:
            transport_mode = TransportMode.WALKING
            duration_minutes = int(distance_km * 12)
            estimated_cost = 0
        elif distance_km <= 10.0:
            transport_mode = TransportMode.TAXI
            duration_minutes = int(distance_km * 3)  # ~20 km/h in city traffic
            # Taxi fare: base fare + per km
            estimated_cost = 100000 + int(distance_km * 30000)
        else:
            transport_mode = TransportMode.DRIVING
            duration_minutes = int(distance_km * 2)  # ~30 km/h average
            # Fuel + car cost estimate
            estimated_cost = int(distance_km * 15000)
        
        # Minimum duration of 5 minutes
        duration_minutes = max(5, duration_minutes)
        
        return TravelInfo(
            from_facility_id=from_facility_id,
            to_facility_id=to_facility_id,
            distance_km=round(distance_km, 2),
            duration_minutes=duration_minutes,
            transport_mode=transport_mode,
            estimated_cost=estimated_cost
        )

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula.
        
        Returns distance in kilometers.
        """
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
