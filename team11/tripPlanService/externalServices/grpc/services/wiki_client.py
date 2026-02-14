"""
Wikipedia/Knowledge Base Client - Fully Mocked with Comprehensive Iranian Places Data
"""
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class WikiClient:
    """
    Fully mocked client for fetching place information
    Contains detailed Wikipedia-style information for Iranian tourist destinations
    """

    def __init__(self):
        logger.info("WikiClient initialized in FULL MOCK mode")
        self._initialize_wiki_data()

    def _initialize_wiki_data(self):
        """Initialize comprehensive Wikipedia-style data for Iranian places"""

        self.wiki_data = {
            # Tehran Province
            'place_tehran_001': {
                'title': 'برج میلاد',
                'description': 'برج میلاد تهران با ارتفاع ۴۳۵ متر، ششمین برج بلند مخابراتی جهان و نماد پایتخت ایران است. این برج در سال ۱۳۸۶ افتتاح شد و دارای رستوران گردان، پلتفرم دید، موزه و مرکز خرید است.',
                'history': 'ساخت برج میلاد در سال ۱۳۷۶ آغاز شد و پس از ۱۰ سال کار، در سال ۱۳۸۶ به بهره‌برداری رسید. این برج توسط معمار محمد رضا حافظی طراحی شده است.',
                'images': [
                    'https://example.com/milad-tower-1.jpg',
                    'https://example.com/milad-tower-2.jpg',
                    'https://example.com/milad-tower-night.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/برج_میلاد',
                'province': 'تهران',
                'location': 'تهران'
            },
            'place_tehran_002': {
                'title': 'کاخ گلستان',
                'description': 'کاخ گلستان، مجموعه کاخ‌های سلطنتی دوره قاجار در تهران و یکی از آثار ثبت‌شده در فهرست میراث جهانی یونسکو است. این مجموعه شامل ۱۷ بنای تاریخی شامل کاخ‌ها، تالارها و موزه‌هاست.',
                'history': 'کاخ گلستان در دوره صفوی بنا شد اما در دوره قاجار به‌ویژه زمان فتحعلی شاه و ناصرالدین شاه گسترش یافت. این مجموعه در سال ۲۰۱۳ به ثبت یونسکو رسید.',
                'images': [
                    'https://example.com/golestan-palace-1.jpg',
                    'https://example.com/golestan-palace-2.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/کاخ_گلستان',
                'province': 'تهران',
                'location': 'تهران'
            },
            'place_tehran_003': {
                'title': 'بازار تجریش',
                'description': 'بازار تجریش یکی از قدیمی‌ترین و معروف‌ترین بازارهای سنتی شمال تهران است که در کنار امامزاده صالح قرار دارد. این بازار مرکز خرید میوه، سبزیجات، ادویه و صنایع دستی است.',
                'history': 'بازار تجریش قدمتی بیش از ۲۰۰ سال دارد و همواره مرکز تجاری روستاهای اطراف بوده است. در دوره پهلوی و پس از آن نوسازی شده اما معماری سنتی خود را حفظ کرده است.',
                'images': [
                    'https://example.com/tajrish-bazaar.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/بازار_تجریش',
                'province': 'تهران',
                'location': 'تهران'
            },

            # Isfahan Province
            'place_isfahan_001': {
                'title': 'میدان نقش جهان',
                'description': 'میدان نقش جهان یا میدان امام، با مساحت ۸۹۶۰۰ متر مربع، دومین میدان بزرگ جهان و یکی از زیباترین میادین تاریخی جهان است. این میدان در سال ۱۹۷۹ به ثبت میراث جهانی یونسکو رسید.',
                'history': 'میدان نقش جهان در زمان شاه عباس اول صفوی (۱۵۹۸-۱۶۲۹) ساخته شد و مرکز شهر جدید اصفهان بود. در اطراف این میدان بناهایی چون مسجد شاه، مسجد شیخ لطف‌الله، کاخ عالی‌قاپو و بازار قیصریه قرار دارد.',
                'images': [
                    'https://example.com/naghsh-jahan-square.jpg',
                    'https://example.com/naghsh-jahan-night.jpg',
                    'https://example.com/naghsh-jahan-fountain.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/میدان_نقش_جهان',
                'province': 'اصفهان',
                'location': 'اصفهان'
            },
            'place_isfahan_002': {
                'title': 'مسجد شیخ لطف‌الله',
                'description': 'مسجد شیخ لطف‌الله یکی از شاهکارهای بی‌نظیر معماری اسلامی و هنر کاشی‌کاری ایرانی است که در ضلع شرقی میدان نقش جهان قرار دارد. این مسجد بدون مناره و حیاط است و مخصوص خاندان سلطنتی بود.',
                'history': 'ساخت این مسجد در سال ۱۶۰۳ میلادی آغاز و در سال ۱۶۱۹ به پایان رسید. نام مسجد به احترام شیخ لطف‌الله میسی، عالم شیعه لبنانی که به درخواست شاه عباس به اصفهان آمد، نامگذاری شده است.',
                'images': [
                    'https://example.com/sheikh-lotfollah-exterior.jpg',
                    'https://example.com/sheikh-lotfollah-dome.jpg',
                    'https://example.com/sheikh-lotfollah-tilework.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/مسجد_شیخ_لطف‌الله',
                'province': 'اصفهان',
                'location': 'اصفهان'
            },
            'place_isfahan_003': {
                'title': 'سی‌وسه‌پل',
                'description': 'سی‌وسه‌پل یا پل الله‌وردی‌خان، یکی از معروف‌ترین پل‌های تاریخی اصفهان بر روی رودخانه زاینده‌رود است. این پل دارای ۳۳ دهانه است و به همین دلیل سی‌وسه‌پل نامیده می‌شود.',
                'history': 'این پل در سال ۱۶۰۲ میلادی به دستور شاه عباس اول و توسط الله‌وردی‌خان، سردار گرجی او، ساخته شد. طول پل ۲۹۵ متر و عرض آن ۱۴ متر است.',
                'images': [
                    'https://example.com/si-o-se-pol-day.jpg',
                    'https://example.com/si-o-se-pol-night.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/سی‌وسه‌پل',
                'province': 'اصفهان',
                'location': 'اصفهان'
            },

            # Fars Province
            'place_fars_001': {
                'title': 'تخت جمشید',
                'description': 'تخت جمشید یا پارسه، پایتخت تشریفاتی امپراتوری هخامنشی است که در ۵۷ کیلومتری شمال شرقی شیراز قرار دارد. این مجموعه در سال ۱۹۷۹ به ثبت میراث جهانی یونسکو رسید.',
                'history': 'ساخت تخت جمشید توسط داریوش بزرگ در حدود ۵۱۸ قبل از میلاد آغاز شد و توسط جانشینانش ادامه یافت. این مجموعه در سال ۳۳۰ قبل از میلاد توسط اسکندر مقدونی به آتش کشیده شد.',
                'images': [
                    'https://example.com/persepolis-main.jpg',
                    'https://example.com/persepolis-stairs.jpg',
                    'https://example.com/persepolis-reliefs.jpg',
                    'https://example.com/persepolis-columns.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/تخت_جمشید',
                'province': 'فارس',
                'location': 'شیراز'
            },
            'place_fars_002': {
                'title': 'مسجد نصیرالملک',
                'description': 'مسجد نصیرالملک یا مسجد صورتی، یکی از زیباترین مساجد ایران است که به خاطر شیشه‌های رنگی خیره‌کننده‌اش معروف است. نور خورشید صبحگاهی که از پنجره‌های رنگی عبور می‌کند، نمایش بی‌نظیری از رنگ‌ها ایجاد می‌کند.',
                'history': 'ساخت این مسجد در سال ۱۲۵۶ هجری قمری به دستور میرزا حسن علی نصیرالملک شیرازی آغاز و در سال ۱۳۰۶ هجری قمری به پایان رسید. معماری این مسجد ترکیبی از معماری قاجار و صفوی است.',
                'images': [
                    'https://example.com/nasir-ol-molk-light.jpg',
                    'https://example.com/nasir-ol-molk-stained-glass.jpg',
                    'https://example.com/nasir-ol-molk-interior.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/مسجد_نصیرالملک',
                'province': 'فارس',
                'location': 'شیراز'
            },
            'place_fars_003': {
                'title': 'باغ ارم',
                'description': 'باغ ارم شیراز یکی از باغ‌های تاریخی و زیبای ایران است که امروزه بخشی از باغ‌های ایرانی ثبت‌شده در میراث جهانی یونسکو است. این باغ محل استقرار دانشکده کشاورزی دانشگاه شیراز نیز هست.',
                'history': 'باغ ارم در دوره صفویه بنا شد اما کاخ کنونی آن در دوره قاجار توسط قوام‌الملک ساخته شد. باغ دارای درختان سرو کهنسال و کاخی با معماری قاجاری است.',
                'images': [
                    'https://example.com/eram-garden-palace.jpg',
                    'https://example.com/eram-garden-pool.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/باغ_ارم',
                'province': 'فارس',
                'location': 'شیراز'
            },

            # Khorasan Razavi Province
            'place_khorasan_001': {
                'title': 'حرم مطهر امام رضا',
                'description': 'حرم مطهر امام رضا (ع) هشتمین امام شیعیان، بزرگترین مسجد جهان بر اساس مساحت و قطب زیارتی مذهبی ایران است. این مجموعه سالانه میزبان میلیون‌ها زائر از سراسر جهان است.',
                'history': 'امام رضا (ع) در سال ۲۰۳ هجری قمری در توس (مشهد کنونی) به شهادت رسید و در همان محل دفن شد. ساخت حرم از دوره هارون‌الرشید آغاز شد و در طول قرون مختلف توسعه یافت.',
                'images': [
                    'https://example.com/imam-reza-shrine-golden-dome.jpg',
                    'https://example.com/imam-reza-shrine-courtyard.jpg',
                    'https://example.com/imam-reza-shrine-night.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/حرم_امام_رضا',
                'province': 'خراسان رضوی',
                'location': 'مشهد'
            },
            'place_khorasan_002': {
                'title': 'آرامگاه فردوسی',
                'description': 'آرامگاه فردوسی، مقبره ابوالقاسم فردوسی، شاعر بزرگ ایرانی و سراینده شاهنامه، در شهر توس واقع شده است. این بنا در سال ۱۳۱۳ هجری شمسی ساخته شد.',
                'history': 'فردوسی در سال ۴۱۶ هجری قمری درگذشت و در باغ خود در توس دفن شد. آرامگاه کنونی در دوره پهلوی با معماری هخامنشی و به طراحی حسینقلی مستعان ساخته شد.',
                'images': [
                    'https://example.com/ferdowsi-tomb-monument.jpg',
                    'https://example.com/ferdowsi-statue.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/آرامگاه_فردوسی',
                'province': 'خراسان رضوی',
                'location': 'توس'
            },

            # Yazd Province
            'place_yazd_001': {
                'title': 'شهر تاریخی یزد',
                'description': 'بافت تاریخی شهر یزد با معماری خشتی منحصر به فرد، یکی از قدیمی‌ترین شهرهای مسکونی جهان و اولین شهر خشتی ثبت شده در میراث جهانی یونسکو است. یزد به شهر بادگیرها معروف است.',
                'history': 'یزد از دوره ساسانیان وجود داشته و در دوره اسلامی به دلیل موقعیت جغرافیایی در مسیر جاده ابریشم رونق یافت. معماری بومی یزد متناسب با آب و هوای گرم و خشک است.',
                'images': [
                    'https://example.com/yazd-old-city-aerial.jpg',
                    'https://example.com/yazd-windcatchers.jpg',
                    'https://example.com/yazd-alley.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/یزد',
                'province': 'یزد',
                'location': 'یزد'
            },
            'place_yazd_002': {
                'title': 'برج‌های سکوت',
                'description': 'دخمه‌های زرتشتی یا برج‌های سکوت، محل‌های دفن مردگان در آیین زرتشتی است که بر روی دو تپه در یزد قرار دارند. این مکان‌ها تا چند دهه پیش مورد استفاده زرتشتیان بود.',
                'history': 'زرتشتیان برای جلوگیری از آلودگی عناصر پاک (خاک، آب، آتش، هوا)، اجساد را در این برج‌ها قرار می‌دادند تا توسط پرندگان درنده پاک‌سازی شوند. این سنت در دهه ۱۳۴۰ متوقف شد.',
                'images': [
                    'https://example.com/towers-of-silence-aerial.jpg',
                    'https://example.com/towers-of-silence-entrance.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/دخمه',
                'province': 'یزد',
                'location': 'یزد'
            },
            'place_yazd_003': {
                'title': 'باغ دولت‌آباد',
                'description': 'باغ دولت‌آباد یزد، یکی از باغ‌های ایرانی ثبت‌شده در میراث جهانی یونسکو است که دارای بلندترین بادگیر خشتی جهان با ارتفاع ۳۳ متر است.',
                'history': 'این باغ در سال ۱۱۶۰ هجری قمری به دستور محمدتقی خان بافقی، حاکم یزد، ساخته شد. باغ دارای یک کاخ هشت‌بهشتی و قنات قدیمی است.',
                'images': [
                    'https://example.com/dowlat-abad-garden.jpg',
                    'https://example.com/dowlat-abad-windcatcher.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/باغ_دولت‌آباد',
                'province': 'یزد',
                'location': 'یزد'
            },

            # Gilan Province
            'place_gilan_001': {
                'title': 'جنگل‌های ابر',
                'description': 'جنگل‌های ابر در ارتفاعات گیلان، یکی از زیباترین جنگل‌های ایران است که اغلب در ابر و مه فرو رفته است. این جنگل بخشی از جنگل‌های هیرکانی است.',
                'history': 'جنگل‌های هیرکانی از بقایای جنگل‌های دوره سوم زمین‌شناسی هستند که قدمتی حدود ۲۵ میلیون ساله دارند. این جنگل‌ها در سال ۲۰۱۹ به ثبت یونسکو رسیدند.',
                'images': [
                    'https://example.com/abr-forest-mist.jpg',
                    'https://example.com/abr-forest-trees.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/جنگل_ابر',
                'province': 'گیلان',
                'location': 'ماسوله'
            },
            'place_gilan_002': {
                'title': 'روستای ماسوله',
                'description': 'ماسوله، روستای پلکانی معروف در ارتفاعات گیلان است که معماری منحصر به فردی دارد. در این روستا، حیاط خانه‌ای، سقف خانه زیرین است.',
                'history': 'ماسوله قدمتی حدود ۱۰۰۰ ساله دارد و در گذشته به دلیل موقعیت جغرافیایی، مرکز تجاری منطقه بود. این روستا یکی از جاذبه‌های اصلی گردشگری ایران است.',
                'images': [
                    'https://example.com/masouleh-village.jpg',
                    'https://example.com/masouleh-stairs.jpg',
                    'https://example.com/masouleh-fog.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/ماسوله',
                'province': 'گیلان',
                'location': 'ماسوله'
            },

            # Kerman Province
            'place_kerman_001': {
                'title': 'کلوت‌های شهداد',
                'description': 'کلوت‌ها یا کویر لوت، یکی از داغ‌ترین نقاط کره زمین و منظره‌ای خارق‌العاده از شهرهای شنی و گلی طبیعی است. این منطقه در سال ۲۰۱۶ به ثبت میراث جهانی یونسکو رسید.',
                'history': 'کلوت‌ها طی هزاران سال توسط فرسایش آب و باد شکل گرفته‌اند. این ساختارهای طبیعی ارتفاعی تا ۵۰ متر دارند و منظره‌ای شبیه شهرهای خالی از سکنه ایجاد می‌کنند.',
                'images': [
                    'https://example.com/kaluts-aerial.jpg',
                    'https://example.com/kaluts-sunset.jpg',
                    'https://example.com/kaluts-landscape.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/کویر_لوت',
                'province': 'کرمان',
                'location': 'شهداد'
            },
            'place_kerman_002': {
                'title': 'باغ شاهزاده ماهان',
                'description': 'باغ شاهزاده، یکی از زیباترین باغ‌های ایرانی در ماهان کرمان است که در دل کویر ساخته شده و جزو میراث جهانی یونسکو است. این باغ دارای آبشارهای مصنوعی و معماری قاجاری است.',
                'history': 'باغ شاهزاده در دوره صفویه پایه‌گذاری و در دوره قاجار توسط عبدالحمید میرزا ناصرالدوله، حاکم کرمان، توسعه یافت. این باغ با استفاده از قنات آبیاری می‌شود.',
                'images': [
                    'https://example.com/shahzadeh-garden-main.jpg',
                    'https://example.com/shahzadeh-garden-fountains.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/باغ_شاهزاده',
                'province': 'کرمان',
                'location': 'ماهان'
            },

            # Khuzestan Province
            'place_khuzestan_001': {
                'title': 'شوش تاریخی',
                'description': 'شوش یا سوسه، یکی از قدیمی‌ترین شهرهای پیوسته مسکونی جهان و پایتخت امپراتوری عیلام است. این محوطه باستانی در سال ۲۰۱۵ به ثبت میراث جهانی یونسکو رسید.',
                'history': 'شوش قدمتی بیش از ۶۰۰۰ سال دارد و مرکز تمدن عیلام بود. در دوره هخامنشیان نیز به عنوان یکی از پایتخت‌های امپراتوری شناخته می‌شد. در این محوطه، کاخ داریوش کشف شده است.',
                'images': [
                    'https://example.com/susa-ruins.jpg',
                    'https://example.com/susa-archaeological-site.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/شوش_(شهر_باستانی)',
                'province': 'خوزستان',
                'location': 'شوش'
            },
            'place_khuzestan_002': {
                'title': 'چغازنبیل',
                'description': 'چغازنبیل، یکی از معدود زیگورات‌های باقی‌مانده از تمدن عیلام و تنها زیگورات موجود در ایران است که در سال ۱۹۷۹ به ثبت میراث جهانی یونسکو رسید.',
                'history': 'این زیگورات در قرن ۱۳ قبل از میلاد توسط اونتاش نپیریشا، پادشاه عیلام، ساخته شد. بنای اصلی پنج طبقه داشت که امروز سه طبقه آن باقی مانده است.',
                'images': [
                    'https://example.com/choghazanbil-ziggurat.jpg',
                    'https://example.com/choghazanbil-aerial.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/چغازنبیل',
                'province': 'خوزستان',
                'location': 'شوش'
            },

            # Hamedan Province
            'place_hamedan_001': {
                'title': 'غار علیصدر',
                'description': 'غار علیصدر، بزرگترین غار آبی جهان است که با قایق قابل گشت است. این غار با طول تقریبی ۱۱ کیلومتر، یکی از شگفت‌انگیزترین جاذبه‌های طبیعی ایران است.',
                'history': 'غار علیصدر میلیون‌ها سال قدمت دارد و طی سال‌ها توسط آب شکل گرفته است. این غار در سال ۱۳۴۲ کشف و در سال ۱۳۵۳ برای گردشگری باز شد.',
                'images': [
                    'https://example.com/alisadr-cave-lake.jpg',
                    'https://example.com/alisadr-cave-boat.jpg',
                    'https://example.com/alisadr-cave-formations.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/غار_علیصدر',
                'province': 'همدان',
                'location': 'کبودرآهنگ'
            },
            'place_hamedan_002': {
                'title': 'آرامگاه بوعلی سینا',
                'description': 'آرامگاه بوعلی سینا، مقبره ابوعلی حسین بن عبدالله بن سینا، دانشمند، فیلسوف و پزشک بزرگ ایرانی است. این بنا در میدان بوعلی همدان قرار دارد.',
                'history': 'بوعلی سینا در سال ۴۲۸ هجری قمری در همدان درگذشت و در همان شهر دفن شد. آرامگاه کنونی در سال ۱۳۳۱ هجری شمسی با معماری مدرن و الهام از برج قابوس ساخته شد.',
                'images': [
                    'https://example.com/avicenna-mausoleum.jpg',
                    'https://example.com/avicenna-tower.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/آرامگاه_بوعلی_سینا',
                'province': 'همدان',
                'location': 'همدان'
            },
            'place_hamedan_003': {
                'title': 'گنجنامه',
                'description': 'گنجنامه، دو کتیبه سنگی از دوره هخامنشیان است که به دستور داریوش بزرگ و خشایارشا در کنار آبشارهای زیبا حک شده است. این کتیبه‌ها به سه زبان باستانی نوشته شده‌اند.',
                'history': 'این کتیبه‌ها در قرن ۵ و ۶ قبل از میلاد حک شده‌اند و در آن‌ها از اهورامزدا و نسب پادشاه یاد شده است. نام گنجنامه به این دلیل است که مردم محلی تصور می‌کردند این نوشته‌ها نقشه گنجی هستند.',
                'images': [
                    'https://example.com/ganjnameh-inscriptions.jpg',
                    'https://example.com/ganjnameh-waterfall.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/گنجنامه',
                'province': 'همدان',
                'location': 'همدان'
            },

            # Kurdistan Province
            'place_kurdistan_001': {
                'title': 'قوری قلعه',
                'description': 'قوری قلعه، روستای پلکانی زیبا در ارتفاعات کردستان است که خانه‌های سنتی کردی آن در دامنه کوه ساخته شده است. این روستا یکی از جاذبه‌های گردشگری کردستان است.',
                'history': 'قوری قلعه قدمتی چند صد ساله دارد و معماری آن نمونه‌ای از سازگاری با طبیعت کوهستانی است. روستا به دلیل منظره زیبا و معماری سنتی توجه گردشگران را جلب کرده است.',
                'images': [
                    'https://example.com/quri-qaleh-village.jpg',
                    'https://example.com/quri-qaleh-houses.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/پالنگان',
                'province': 'کردستان',
                'location': 'پالنگان'
            },
            'place_kurdistan_002': {
                'title': 'دریاچه زریوار',
                'description': 'دریاچه زریوار، زیباترین دریاچه آب شیرین ایران در مریوان کردستان است. این دریاچه در ارتفاع ۱۲۸۵ متری از سطح دریا قرار دارد و اطرافش پوشیده از جنگل بلوط است.',
                'history': 'دریاچه زریوار به صورت طبیعی شکل گرفته و قدمتی هزاران ساله دارد. این دریاچه همواره مرکز فرهنگ و افسانه‌های محلی کردستان بوده است.',
                'images': [
                    'https://example.com/zarivar-lake-panorama.jpg',
                    'https://example.com/zarivar-lake-sunset.jpg',
                    'https://example.com/zarivar-lake-boats.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/دریاچه_زریوار',
                'province': 'کردستان',
                'location': 'مریوان'
            },

            # Kermanshah Province
            'place_kermanshah_001': {
                'title': 'طاق بستان',
                'description': 'طاق بستان، مجموعه‌ای از نقش برجسته‌های سنگی دوره ساسانی است که در کنار چشمه‌ای طبیعی در کرمانشاه قرار دارد. این اثر در سال ۲۰۱۸ به ثبت میراث جهانی یونسکو رسید.',
                'history': 'این نقوش در دوره اردشیر دوم، شاپور دوم و خسرو پرویز (قرن ۳ تا ۷ میلادی) حک شده‌اند و صحنه‌هایی از شکار، تاج‌گذاری و جنگ را نشان می‌دهند.',
                'images': [
                    'https://example.com/taq-bostan-reliefs.jpg',
                    'https://example.com/taq-bostan-hunting.jpg',
                    'https://example.com/taq-bostan-spring.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/طاق_بستان',
                'province': 'کرمانشاه',
                'location': 'کرمانشاه'
            },
            'place_kermanshah_002': {
                'title': 'بیستون',
                'description': 'سنگ‌نبشته بیستون، بزرگترین کتیبه باستانی جهان است که به دستور داریوش بزرگ در ارتفاع ۱۰۰ متری کوه بیستون حک شده است. این اثر در سال ۲۰۰۶ به ثبت میراث جهانی یونسکو رسید.',
                'history': 'این کتیبه در سال ۵۲۰ قبل از میلاد حک شد و داستان به قدرت رسیدن داریوش را به سه زبان باستانی (پارسی باستان، عیلامی و بابلی) نقل می‌کند. رمزگشایی این کتیبه کلید فهم خط میخی شد.',
                'images': [
                    'https://example.com/bisotun-inscription.jpg',
                    'https://example.com/bisotun-mountain.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/کتیبه_بیستون',
                'province': 'کرمانشاه',
                'location': 'بیستون'
            },

            # Ardabil Province
            'place_ardabil_001': {
                'title': 'کوه سبلان',
                'description': 'کوه سبلان با ارتفاع ۴۸۱۱ متر، سومین قله بلند ایران و یکی از قله‌های آتشفشانی خاموش است. در دهانه این آتشفشان، دریاچه‌ای زیبا به نام دریاچه گل قرار دارد.',
                'history': 'کوه سبلان در دوره چهارم زمین‌شناسی فعالیت آتشفشانی داشته است. این کوه در فرهنگ و ادبیات ایران جایگاه ویژه‌ای دارد و در شاهنامه فردوسی نیز از آن یاد شده است.',
                'images': [
                    'https://example.com/sabalan-peak.jpg',
                    'https://example.com/sabalan-lake.jpg',
                    'https://example.com/sabalan-crater.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/سبلان',
                'province': 'اردبیل',
                'location': 'سرعین'
            },
            'place_ardabil_002': {
                'title': 'چشمه آبگرم سرعین',
                'description': 'سرعین، شهر چشمه‌های آب گرم معدنی است که در دامنه کوه سبلان قرار دارد. این آب‌های معدنی خواص درمانی دارند و سالانه میلیون‌ها گردشگر به این شهر سفر می‌کنند.',
                'history': 'چشمه‌های آبگرم سرعین از دیرباز شناخته شده بودند اما در چند دهه اخیر به‌عنوان مقصد گردشگری سلامت توسعه یافته‌اند. این شهر بیش از ۹ چشمه آبگرم فعال دارد.',
                'images': [
                    'https://example.com/sarein-hot-spring.jpg',
                    'https://example.com/sarein-pools.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org/wiki/سرعین',
                'province': 'اردبیل',
                'location': 'سرعین'
            },

            # Generic/Default entries for other places
            'default': {
                'title': 'مکان گردشگری ایران',
                'description': 'یکی از مکان‌های دیدنی و جذاب ایران که ارزش بازدید دارد.',
                'history': 'این مکان دارای سابقه تاریخی و فرهنگی غنی است.',
                'images': [
                    'https://example.com/iran-tourism.jpg'
                ],
                'wiki_url': 'https://fa.wikipedia.org',
                'province': 'ایران',
                'location': 'ایران'
            }
        }

    def get_place_info(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a place

        Args:
            place_id: Place identifier

        Returns:
            Dictionary with title, description, history, images, wiki_url, province, location
        """
        logger.info(f"Fetching wiki info for place: {place_id}")

        # Check if we have specific data for this place
        if place_id in self.wiki_data:
            return self.wiki_data[place_id]

        # Return default info if place not found
        logger.warning(f"No wiki data found for {place_id}, returning default info")
        return self.wiki_data['default']

    def search_by_province(self, province: str) -> List[Dict]:
        """
        Search for places by province name

        Args:
            province: Province name in Persian

        Returns:
            List of place info dictionaries
        """
        results = []
        for place_id, info in self.wiki_data.items():
            if place_id != 'default' and info.get('province') == province:
                result = info.copy()
                result['place_id'] = place_id
                results.append(result)

        return results

    def get_featured_places(self, limit: int = 10) -> List[Dict]:
        """
        Get a list of featured/popular places

        Args:
            limit: Maximum number of places to return

        Returns:
            List of featured place info
        """
        featured = []
        for place_id, info in self.wiki_data.items():
            if place_id != 'default':
                result = info.copy()
                result['place_id'] = place_id
                featured.append(result)

        return featured[:limit]


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    client = WikiClient()

    # Test 1: Get info for specific place
    print("\n=== Test 1: Get info for Naghsh-e Jahan ===")
    info = client.get_place_info('place_isfahan_001')
    if info:
        print(f"Title: {info['title']}")
        print(f"Province: {info['province']}")
        print(f"Description: {info['description'][:100]}...")
        print(f"Images: {len(info['images'])} available")

    # Test 2: Get info for Persepolis
    print("\n=== Test 2: Get info for Persepolis ===")
    info = client.get_place_info('place_fars_001')
    if info:
        print(f"Title: {info['title']}")
        print(f"History: {info['history'][:100]}...")
        print(f"Wiki URL: {info['wiki_url']}")

    # Test 3: Search by province
    print("\n=== Test 3: Places in Isfahan ===")
    isfahan_places = client.search_by_province('اصفهان')
    for place in isfahan_places:
        print(f"- {place['title']} ({place['place_id']})")

    # Test 4: Get featured places
    print("\n=== Test 4: Featured places ===")
    featured = client.get_featured_places(limit=5)
    for place in featured:
        print(f"- {place['title']} - {place['province']}")

    # Test 5: Unknown place (default response)
    print("\n=== Test 5: Unknown place ID ===")
    info = client.get_place_info('place_unknown_999')
    if info:
        print(f"Title: {info['title']}")
        print(f"Description: {info['description']}")

    print(f"\n=== Summary ===")
    print(f"Total places with detailed info: {len(client.wiki_data) - 1}")  # -1 for default