const shuffle = (array: string[]) => array.sort(() => Math.random() - 0.5);

const rawImages = [
  '/team11/images/baz1.jpg', '/team11/images/baz2.jpg', '/team11/images/baz3.jpg', '/team11/images/baz4.jpg', '/team11/images/baz5.jpg',
  '/team11/images/his1.jpg', '/team11/images/his2.jpg', '/team11/images/his3.jpg', '/team11/images/his4.jpg', '/team11/images/his5.jpg',
  '/team11/images/his6.jpg', '/team11/images/his7.jpg', '/team11/images/his8.jpg', '/team11/images/his9.jpg', '/team11/images/his10.jpg',
  '/team11/images/his11.jpg', '/team11/images/his12.jpg', '/team11/images/his13.jpg', '/team11/images/his14.jpg',
  '/team11/images/maz1.jpg', '/team11/images/maz2.jpg', '/team11/images/maz3.jpg',
  '/team11/images/nat1.jpg', '/team11/images/nat2.jpg', '/team11/images/nat3.jpg', '/team11/images/nat4.jpg', '/team11/images/nat5.jpg',
  '/team11/images/nat6.jpg', '/team11/images/nat7.jpg', '/team11/images/nat9.jpg', '/team11/images/nat10.jpg',
  '/team11/images/rod1.jpg', '/team11/images/rod2.jpg', '/team11/images/rod3.jpg', '/team11/images/rod4.jpg', '/team11/images/rod5.jpg',
  '/team11/images/sea1.jpg', '/team11/images/sea2.jpg', '/team11/images/sea3.jpg', '/team11/images/sea4.jpg'
];
export const SCROLLING_IMAGES = shuffle([...rawImages]);

export const PROVINCES_DETAILS: Record<string, { province: string; name: string; image: string }> = {
  alborz: { province: 'alborz', name: 'البرز', image: 'https://cdn.mashreghnews.ir/d/2020/05/11/4/2793271.jpg' },
  ardabil: { province: 'ardabil', name: 'اردبیل', image: 'https://ammi.ir/wp-content/uploads/1__2_-Medium-16.jpg' },
  azarbaijan_east: { province: 'azarbaijan_east', name: 'آذربایجان شرقی', image: 'https://sepanja.com/blog/wp-content/uploads/2021/08/Shah-goli.jpg' },
  azarbaijan_west: { province: 'azarbaijan_west', name: 'آذربایجان غربی', image: 'https://ammi.ir/wp-content/uploads/26__2_-Medium.jpg' },
  bushehr: { province: 'bushehr', name: 'بوشهر', image: 'https://ammi.ir/wp-content/uploads/1__20_-39.jpg' },
  chaharmahal_bakhtiari: { province: 'chaharmahal_bakhtiari', name: 'چهارمحال و بختیاری', image: 'https://ammi.ir/wp-content/uploads/1__5_-208.jpg' },
  fars: { province: 'fars', name: 'فارس', image: 'https://ammi.ir/wp-content/uploads/1__3__2-Medium-23.jpg' },
  gilan: { province: 'gilan', name: 'گیلان', image: 'https://ammi.ir/wp-content/uploads/1__10__2-Medium-34.jpg' },
  golestan: { province: 'golestan', name: 'گلستان', image: 'https://ammi.ir/wp-content/uploads/1__10__2-67.jpg' },
  hamadan: { province: 'hamadan', name: 'همدان', image: 'https://cdn.alibaba.ir/ostorage/alibaba-mag/wp-content/uploads/2020/03/0-850%C3%97440-Alisadr-Cave.jpg' },
  hormozgan: { province: 'hormozgan', name: 'هرمزگان', image: 'https://ammi.ir/wp-content/uploads/1-__13_-22.jpg' },
  ilam: { province: 'ilam', name: 'ایلام', image: 'https://img9.irna.ir/d/r1/2023/05/16/4/170372442.jpg?ts=1684255549890' },
  isfahan: { province: 'isfahan', name: 'اصفهان', image: 'https://ammi.ir/wp-content/uploads/1__5__result-24.jpg' },
  kerman: { province: 'kerman', name: 'کرمان', image: 'https://www.mizan.news/wp-content/uploads/2022/01/1542508_141.jpg' },
  kermanshah: { province: 'kermanshah', name: 'کرمانشاه', image: 'https://ammi.ir/wp-content/uploads/1__11_-127.jpg' },
  khorasan_north: { province: 'khorasan_north', name: 'خراسان شمالی', image: 'https://ammi.ir/wp-content/uploads/1__20_-97.jpg' },
  khorasan_razavi: { province: 'khorasan_razavi', name: 'خراسان رضوی', image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcScvJghkXJNuFJFHZ13DMYA0PwyDOGEQTzFSQ&s' },
  khorasan_south: { province: 'khorasan_south', name: 'خراسان جنوبی', image: 'https://ammi.ir/wp-content/uploads/1__9_-242.jpg' },
  khuzestan: { province: 'khuzestan', name: 'خوزستان', image: 'https://ammi.ir/wp-content/uploads/1__25_-25.jpg' },
  kohgiluyeh_boyer_ahmad: { province: 'kohgiluyeh_boyer_ahmad', name: 'کهگیلویه و بویراحمد', image: 'https://ammi.ir/wp-content/uploads/4-2.jpg' },
  kurdistan: { province: 'kurdistan', name: 'کردستان', image: 'https://ammi.ir/wp-content/uploads/1__5_-121.jpg' },
  lorestan: { province: 'lorestan', name: 'لرستان', image: 'https://ammi.ir/wp-content/uploads/1__15_-Medium-33.jpg' },
  markazi: { province: 'markazi', name: 'مرکزی', image: 'https://ammi.ir/wp-content/uploads/1__2__result_2-13.jpg' },
  mazandaran: { province: 'mazandaran', name: 'مازندران', image: 'https://ammi.ir/wp-content/uploads/1-__14_-18.jpg' },
  qazvin: { province: 'qazvin', name: 'قزوین', image: 'https://ammi.ir/wp-content/uploads/1-__6_-40.jpg' },
  qom: { province: 'qom', name: 'قم', image: 'https://ammi.ir/wp-content/uploads/1__11_-92.jpg' },
  semnan: { province: 'semnan', name: 'سمنان', image: 'https://ammi.ir/wp-content/uploads/1__3__2-92.jpg' },
  sistan_baluchestan: { province: 'sistan_baluchestan', name: 'سیستان و بلوچستان', image: 'https://ammi.ir/wp-content/uploads/1__13_-200.jpg' },
  tehran: { province: 'tehran', name: 'تهران', image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQqYX0HTGKPhd4cvPavmQ6_yW14uReWkvJkog&s' },
  yazd: { province: 'yazd', name: 'یزد', image: 'https://ammi.ir/wp-content/uploads/1__15__result-40.jpg' },
  zanjan: { province: 'zanjan', name: 'زنجان', image: 'https://ammi.ir/wp-content/uploads/1-__22_-4.jpg' },
};

export const CITIES_MAP: Record<string, { value: string; label: string }[]> = {
  // استان البرز
  alborz: [
    { value: 'karaj', label: 'کرج' },
    { value: 'kamal_shahr', label: 'کمال‌شهر' },
    { value: 'nazarabad', label: 'نظرآباد' },
    { value: 'mohammadshahr', label: 'محمدشهر' },
    { value: 'hashtgerd', label: 'هشتگرد' },
    { value: 'eshtehard', label: 'اشتهارد' },
    { value: 'fardis', label: 'فردیس' },
    { value: 'mahdasht', label: 'مه‌دشت' },
    { value: 'meshkin_dasht', label: 'مشکیندشت' },
    { value: 'chaharbagh', label: 'چهارباغ' },
    { value: 'golsar', label: 'گلسار' },
    { value: 'kuhsar', label: 'کوهسار' },
    { value: 'taleqan', label: 'طالقان' },
    { value: 'asara', label: 'آسارا' },
    { value: 'tankaman', label: 'تنکمان' }
  ],

  // استان اردبیل
  ardabil: [
    { value: 'ardabil', label: 'اردبیل' },
    { value: 'parsabad', label: 'پارس‌آباد' },
    { value: 'meshginshahr', label: 'مشگین‌شهر' },
    { value: 'khalkhal', label: 'خلخال' },
    { value: 'germi', label: 'گرمی' },
    { value: 'bileh_savar', label: 'بیله‌سوار' },
    { value: 'namin', label: 'نمین' },
    { value: 'nir', label: 'نیر' },
    { value: 'sareyn', label: 'سرعین' },
    { value: 'kivi', label: 'کیوی' },
    { value: 'aslan_duz', label: 'اصلاندوز' },
    { value: 'ab_i_beyglu', label: 'آبی‌بیگلو' },
    { value: 'hashatjin', label: 'هشتجین' },
    { value: 'lahrud', label: 'لاهرود' },
    { value: 'hir', label: 'هیر' }
  ],

  // استان آذربایجان شرقی
  azarbaijan_east: [
    { value: 'tabriz', label: 'تبریز' },
    { value: 'maragheh', label: 'مراغه' },
    { value: 'marand', label: 'مرند' },
    { value: 'ahar', label: 'اهر' },
    { value: 'bonab', label: 'بناب' },
    { value: 'sarāb', label: 'سراب' },
    { value: 'miyaneh', label: 'میانه' },
    { value: 'azarshahr', label: 'آذرشهر' },
    { value: 'shabestar', label: 'شبستر' },
    { value: 'hashtrud', label: 'هشترود' },
    { value: 'jolfa', label: 'جلفا' },
    { value: 'bostanabad', label: 'بستان‌آباد' },
    { value: 'malekan', label: 'ملکان' },
    { value: 'oskou', label: 'اسکو' },
    { value: 'heris', label: 'هریس' }
  ],

  // استان آذربایجان غربی
  azarbaijan_west: [
    { value: 'urmia', label: 'ارومیه' },
    { value: 'khoy', label: 'خوی' },
    { value: 'maku', label: 'ماکو' },
    { value: 'mahabad', label: 'مهاباد' },
    { value: 'miandoab', label: 'میاندوآب' },
    { value: 'salmas', label: 'سلماس' },
    { value: 'piranshahr', label: 'پیرانشهر' },
    { value: 'naqadeh', label: 'نقده' },
    { value: 'takab', label: 'تکاب' },
    { value: 'sardasht', label: 'سردشت' },
    { value: 'shahindezh', label: 'شاهیندژ' },
    { value: 'bukan', label: 'بوکان' },
    { value: 'chaldoran', label: 'چالدران' },
    { value: 'poldasht', label: 'پلدشت' },
    { value: 'showt', label: 'شوط' }
  ],

  // استان بوشهر
  bushehr: [
    { value: 'bushehr', label: 'بوشهر' },
    { value: 'borazjan', label: 'برازجان' },
    { value: 'bandar_ganaveh', label: 'بندر گناوه' },
    { value: 'bandar_kangan', label: 'بندر کنگان' },
    { value: 'khormoj', label: 'خورموج' },
    { value: 'jam', label: 'جم' },
    { value: 'bandar_deylam', label: 'بندر دیلم' },
    { value: 'bandar_deyr', label: 'بندر دیر' },
    { value: 'asaluyeh', label: 'عسلویه' },
    { value: 'ahram', label: 'اهرم' },
    { value: 'kaki', label: 'کاکی' },
    { value: 'bandar_rig', label: 'بندر ریگ' },
    { value: 'shabankareh', label: 'شبانکاره' },
    { value: 'delvar', label: 'دلوار' },
    { value: 'kharg', label: 'خارک' }
  ],

  // استان چهارمحال و بختیاری
  chaharmahal_bakhtiari: [
    { value: 'shahr_e_kord', label: 'شهرکرد' },
    { value: 'borujen', label: 'بروجن' },
    { value: 'lordegan', label: 'لردگان' },
    { value: 'farrokh_shahr', label: 'فرخ‌شهر' },
    { value: 'farsan', label: 'فارسان' },
    { value: 'hafshejan', label: 'هفشجان' },
    { value: 'junqan', label: 'جونقان' },
    { value: 'saman', label: 'سامان' },
    { value: 'ben', label: 'بن' },
    { value: 'ardal', label: 'اردل' },
    { value: 'boldaji', label: 'بلداجی' },
    { value: 'naqneh', label: 'نقنه' },
    { value: 'gandoman', label: 'گندمان' },
    { value: 'babaheydar', label: 'باباحیدر' },
    { value: 'kian', label: 'کیان' }
  ],

  // استان فارس
  fars: [
    { value: 'shiraz', label: 'شیراز' },
    { value: 'marvdasht', label: 'مرودشت' },
    { value: 'jahrom', label: 'جهرم' },
    { value: 'fasa', label: 'فسا' },
    { value: 'kazerun', label: 'کازرون' },
    { value: 'darab', label: 'داراب' },
    { value: 'abadeh', label: 'آباده' },
    { value: 'larestan', label: 'لارستان' },
    { value: 'eqlid', label: 'اقلید' },
    { value: 'neyriz', label: 'نی‌ریز' },
    { value: 'estahban', label: 'استهبان' },
    { value: 'firuzabad', label: 'فیروزآباد' },
    { value: 'lamerd', label: 'لامرد' },
    { value: 'khorrambid', label: 'خرم‌بید' },
    { value: 'khonj', label: 'خنج' }
  ],

  // استان گیلان
  gilan: [
    { value: 'rasht', label: 'رشت' },
    { value: 'bandar_anzali', label: 'بندر انزلی' },
    { value: 'lahijan', label: 'لاهیجان' },
    { value: 'talesh', label: 'تالش' },
    { value: 'langarud', label: 'لنگرود' },
    { value: 'soumeh_sara', label: 'صومعه‌سرا' },
    { value: 'astara', label: 'آستارا' },
    { value: 'astaneh_ashrafiyeh', label: 'آستانه اشرفیه' },
    { value: 'rudsar', label: 'رودسر' },
    { value: 'fuman', label: 'فومن' },
    { value: 'masal', label: 'ماسال' },
    { value: 'rezvanshahr', label: 'رضوانشهر' },
    { value: 'siyahkal', label: 'سیاهکل' },
    { value: 'shaft', label: 'شفت' },
    { value: 'rudbar', label: 'رودبار' }
  ],

  // استان گلستان
  golestan: [
    { value: 'gorgan', label: 'گرگان' },
    { value: 'gonbad_kavous', label: 'گنبد کاووس' },
    { value: 'bandar_torkaman', label: 'بندر ترکمن' },
    { value: 'aliabad_katul', label: 'علی‌آباد کتول' },
    { value: 'aq_qala', label: 'آق‌قلا' },
    { value: 'kordkuy', label: 'کردکوی' },
    { value: 'azadshahr', label: 'آزادشهر' },
    { value: 'kalaleh', label: 'کلاله' },
    { value: 'ramian', label: 'رامیان' },
    { value: 'minudasht', label: 'مینودشت' },
    { value: 'gomishan', label: 'گمیشان' },
    { value: 'maraveh_tappeh', label: 'مراوه‌تپه' },
    { value: 'galikash', label: 'گالیکش' }
  ],

  // استان همدان
  hamadan: [
    { value: 'hamadan', label: 'همدان' },
    { value: 'malayer', label: 'ملایر' },
    { value: 'nahavand', label: 'نهاوند' },
    { value: 'asadabad', label: 'اسدآباد' },
    { value: 'toycerkan', label: 'تویسرکان' },
    { value: 'kabudarahang', label: 'کبودرآهنگ' },
    { value: 'bahar', label: 'بهار' },
    { value: 'razan', label: 'رزن' },
    { value: 'lalejin', label: 'لالجین' },
    { value: 'famenin', label: 'فامنین' },
    { value: 'samen', label: 'سامن' },
    { value: 'qorveh_darajerdi', label: 'قروه درجزین' },
    { value: 'goltappeh', label: 'گلتپه' },
    { value: 'maryanaj', label: 'مریانج' },
    { value: 'juraqan', label: 'جورقان' }
  ],

  // استان هرمزگان
  hormozgan: [
    { value: 'bandar_abbas', label: 'بندرعباس' },
    { value: 'minab', label: 'میناب' },
    { value: 'qeshm', label: 'قشم' },
    { value: 'bandar_lengeh', label: 'بندر لنگه' },
    { value: 'kish', label: 'کیش' },
    { value: 'haji_abad', label: 'حاجی‌آباد' },
    { value: 'rudan', label: 'رودان' },
    { value: 'bastak', label: 'بستک' },
    { value: 'bandar_khamir', label: 'بندر خمیر' },
    { value: 'parsian', label: 'پارسیان' },
    { value: 'bandar_jask', label: 'بندر جاسک' },
    { value: 'abumusa', label: 'ابوموسی' },
    { value: 'hengan', label: 'هنگام' },
    { value: 'laft', label: 'لافت' }
  ],

  // استان ایلام
  ilam: [
    { value: 'ilam', label: 'ایلام' },
    { value: 'dehloran', label: 'دهلران' },
    { value: 'ivan', label: 'ایوان' },
    { value: 'abdanan', label: 'آبدانان' },
    { value: 'darreh_shahr', label: 'دره‌شهر' },
    { value: 'mehran', label: 'مهران' },
    { value: 'sarableh', label: 'سرابله' },
    { value: 'arkanaz', label: 'آرکاناز' },
    { value: 'badreh', label: 'بدره' },
    { value: 'malekshahi', label: 'ملکشاهی' },
    { value: 'maymeh', label: 'میمه' },
    { value: 'sirvan', label: 'سیروان' },
    { value: 'chavar', label: 'چوار' },
    { value: 'eyvan', label: 'ایوان' }
  ],

  // استان اصفهان
  isfahan: [
    { value: 'isfahan', label: 'اصفهان' },
    { value: 'kashan', label: 'کاشان' },
    { value: 'khomeyni_shahr', label: 'خمینی‌شهر' },
    { value: 'najafabad', label: 'نجف‌آباد' },
    { value: 'shahreza', label: 'شهرضا' },
    { value: 'mobarakeh', label: 'مبارکه' },
    { value: 'golpayegan', label: 'گلپایگان' },
    { value: 'fereydan', label: 'فریدن' },
    { value: 'aran_va_bidgol', label: 'آران و بیدگل' },
    { value: 'khomein', label: 'خمین' },
    { value: 'shahin_shahr', label: 'شاهین‌شهر' },
    { value: 'falavarjan', label: 'فلاورجان' },
    { value: 'tiran', label: 'تیران' },
    { value: 'naeen', label: 'نائین' },
    { value: 'natanz', label: 'نطنز' }
  ],

  // استان کرمان
  kerman: [
    { value: 'kerman', label: 'کرمان' },
    { value: 'sirjan', label: 'سیرجان' },
    { value: 'rafsanjan', label: 'رفسنجان' },
    { value: 'bam', label: 'بم' },
    { value: 'jiroft', label: 'جیرفت' },
    { value: 'zarand', label: 'زرند' },
    { value: 'bardsir', label: 'بردسیر' },
    { value: 'kahnuj', label: 'کهنوج' },
    { value: 'anar', label: 'انار' },
    { value: 'baft', label: 'بافت' },
    { value: 'shahr_babak', label: 'شهر بابک' },
    { value: 'manujan', label: 'منوجان' },
    { value: 'rudbar_jonub', label: 'رودبار جنوب' },
    { value: 'qaleh_ganj', label: 'قلعه گنج' },
    { value: 'ravar', label: 'راور' }
  ],

  // استان کرمانشاه
  kermanshah: [
    { value: 'kermanshah', label: 'کرمانشاه' },
    { value: 'eslamabad_e_gharb', label: 'اسلام‌آباد غرب' },
    { value: 'javanrud', label: 'جوانرود' },
    { value: 'kangavar', label: 'کنگاور' },
    { value: 'paveh', label: 'پاوه' },
    { value: 'sarpol_zahab', label: 'سرپل ذهاب' },
    { value: 'sonqor', label: 'سنقر' },
    { value: 'qasr_e_shirin', label: 'قصر شیرین' },
    { value: 'gilanegharb', label: 'گیلانغرب' },
    { value: 'harsin', label: 'هرسین' },
    { value: 'sahneh', label: 'صحنه' },
    { value: 'ravansar', label: 'روانسر' },
    { value: 'dalahu', label: 'دالاهو' },
    { value: 'salas_babajani', label: 'ثلاث باباجانی' }
  ],

  // استان خراسان شمالی
  khorasan_north: [
    { value: 'bojnurd', label: 'بجنورد' },
    { value: 'esfarayen', label: 'اسفراین' },
    { value: 'shirvan', label: 'شیروان' },
    { value: 'ashkhaneh', label: 'آشخانه' },
    { value: 'jajarm', label: 'جاجرم' },
    { value: 'faruj', label: 'فاروج' },
    { value: 'garmeh', label: 'گرمه' },
    { value: 'raz', label: 'راز' },
    { value: 'safiabad', label: 'صفی‌آباد' },
    { value: 'ghanchi', label: 'قانچی' }
  ],

  // استان خراسان رضوی
  khorasan_razavi: [
    { value: 'mashhad', label: 'مشهد' },
    { value: 'neyshabur', label: 'نیشابور' },
    { value: 'sabzevar', label: 'سبزوار' },
    { value: 'torghabeh', label: 'طرقبه' },
    { value: 'shandiz', label: 'شاندیز' },
    { value: 'quchan', label: 'قوچان' },
    { value: 'torbat_e_heydarieh', label: 'تربت حیدریه' },
    { value: 'kashmar', label: 'کاشمر' },
    { value: 'gonabad', label: 'گناباد' },
    { value: 'torbat_e_jam', label: 'تربت جام' },
    { value: 'taybad', label: 'تایباد' },
    { value: 'fariman', label: 'فریمان' },
    { value: 'kalat', label: 'کلات' },
    { value: 'chenaran', label: 'چناران' },
    { value: 'sarakhs', label: 'سرخس' }
  ],

  // استان خراسان جنوبی
  khorasan_south: [
    { value: 'birjand', label: 'بیرجند' },
    { value: 'qayen', label: 'قائن' },
    { value: 'tabas', label: 'طبس' },
    { value: 'ferdows', label: 'فردوس' },
    { value: 'nebandan', label: 'نهبندان' },
    { value: 'sarbisheh', label: 'سربیشه' },
    { value: 'darmian', label: 'درمیان' },
    { value: 'boshruyeh', label: 'بشرویه' },
    { value: 'saraqan', label: 'سرایان' },
    { value: 'zirkuh', label: 'زیرکوه' },
    { value: 'khusf', label: 'خوسف' }
  ],

  // استان خوزستان
  khuzestan: [
    { value: 'ahvaz', label: 'اهواز' },
    { value: 'abadan', label: 'آبادان' },
    { value: 'khorramshahr', label: 'خرمشهر' },
    { value: 'dezful', label: 'دزفول' },
    { value: 'masjed_solayman', label: 'مسجد سلیمان' },
    { value: 'shushtar', label: 'شوشتر' },
    { value: 'bandar_mahshahr', label: 'بندر ماهشهر' },
    { value: 'izeh', label: 'ایذه' },
    { value: 'behbahan', label: 'بهبهان' },
    { value: 'ramhormoz', label: 'رامهرمز' },
    { value: 'shush', label: 'شوش' },
    { value: 'omidiyeh', label: 'امیدیه' },
    { value: 'andimeshk', label: 'اندیمشک' },
    { value: 'hendijan', label: 'هندیجان' },
    { value: 'ramshir', label: 'رامشیر' }
  ],

  // استان کهگیلویه و بویراحمد
  kohgiluyeh_boyer_ahmad: [
    { value: 'yasuj', label: 'یاسوج' },
    { value: 'dehdasht', label: 'دهدشت' },
    { value: 'dogonbadan', label: 'دوگنبدان' },
    { value: 'likak', label: 'لیکک' },
    { value: 'choram', label: 'چرام' },
    { value: 'sugh', label: 'سوق' },
    { value: 'bahmai', label: 'بهمئی' },
    { value: 'landeh', label: 'لنده' },
    { value: 'gachsaran', label: 'گچساران' },
    { value: 'basht', label: 'باشت' }
  ],

  // استان کردستان
  kurdistan: [
    { value: 'sanandaj', label: 'سنندج' },
    { value: 'saqqez', label: 'سقز' },
    { value: 'marivan', label: 'مریوان' },
    { value: 'baneh', label: 'بانه' },
    { value: 'qorveh', label: 'قروه' },
    { value: 'bijar', label: 'بیجار' },
    { value: 'kamyaran', label: 'کامیاران' },
    { value: 'divandarreh', label: 'دیواندره' },
    { value: 'dehgolan', label: 'دهگلان' },
    { value: 'sarwabad', label: 'سروآباد' }
  ],

  // استان لرستان
  lorestan: [
    { value: 'khorramabad', label: 'خرم‌آباد' },
    { value: 'borujerd', label: 'بروجرد' },
    { value: 'dorud', label: 'دورود' },
    { value: 'kuhdasht', label: 'کوهدشت' },
    { value: 'aligudarz', label: 'الیگودرز' },
    { value: 'azna', label: 'ازنا' },
    { value: 'nurabad', label: 'نورآباد' },
    { value: 'poldokhtar', label: 'پلدختر' },
    { value: 'selseleh', label: 'سلسله' },
    { value: 'delfan', label: 'دلفان' }
  ],

  // استان مرکزی
  markazi: [
    { value: 'arak', label: 'اراک' },
    { value: 'saveh', label: 'ساوه' },
    { value: 'khomein', label: 'خمین' },
    { value: 'mahallat', label: 'محلات' },
    { value: 'delijan', label: 'دلیجان' },
    { value: 'tafresh', label: 'تفرش' },
    { value: 'ashtian', label: 'آشتیان' },
    { value: 'shazand', label: 'شازند' },
    { value: 'komijan', label: 'کمیجان' },
    { value: 'zarandieh', label: 'زرندیه' },
    { value: 'mamuniyeh', label: 'مامونیه' },
    { value: 'ghahramankand', label: 'قهرمانکند' },
    { value: 'khenejin', label: 'خنجین' }
  ],

  // استان مازندران
  mazandaran: [
    { value: 'sari', label: 'ساری' },
    { value: 'amol', label: 'آمل' },
    { value: 'babol', label: 'بابل' },
    { value: 'qaemshahr', label: 'قائمشهر' },
    { value: 'behshahr', label: 'بهشهر' },
    { value: 'noshahr', label: 'نوشهر' },
    { value: 'chalus', label: 'چالوس' },
    { value: 'ramsar', label: 'رامسر' },
    { value: 'tonekabon', label: 'تنکابن' },
    { value: 'mahmudabad', label: 'محمودآباد' },
    { value: 'nowshahr', label: 'نوشهر' },
    { value: 'nur', label: 'نور' },
    { value: 'babolkar', label: 'بابلکر' },
    { value: 'feridonkenar', label: 'فریدونکنار' },
    { value: 'juybar', label: 'جویبار' }
  ],

  // استان قزوین
  qazvin: [
    { value: 'qazvin', label: 'قزوین' },
    { value: 'alvand', label: 'الوند' },
    { value: 'takestan', label: 'تاکستان' },
    { value: 'boyin_zahra', label: 'بوئین‌زهرا' },
    { value: 'abeyek', label: 'آبیک' },
    { value: 'shal', label: 'شال' },
    { value: 'khoremand', label: 'خرمدشت' },
    { value: 'avaj', label: 'آوج' },
    { value: 'mohammadiyeh', label: 'محمدیه' },
    { value: 'esfarvarin', label: 'اسفرورین' },
    { value: 'danesfahan', label: 'دانسفهان' }
  ],

  // استان قم
  qom: [
    { value: 'qom', label: 'قم' },
    { value: 'qanavat', label: 'قنوات' },
    { value: 'jafariyeh', label: 'جعفریه' },
    { value: 'kahak', label: 'کهک' },
    { value: 'dastjerd', label: 'دستجرد' },
    { value: 'salafchegan', label: 'سلفچگان' }
  ],

  // استان سمنان
  semnan: [
    { value: 'semnan', label: 'سمنان' },
    { value: 'shahroud', label: 'شاهرود' },
    { value: 'damghan', label: 'دامغان' },
    { value: 'garmsar', label: 'گرمسار' },
    { value: 'meyami', label: 'میامی' },
    { value: 'mahdishahr', label: 'مهدیشهر' },
    { value: 'eyvanaki', label: 'ایوانکی' },
    { value: 'bastam', label: 'بسطام' },
    { value: 'sorkheh', label: 'سرخه' },
    { value: 'kohanabad', label: 'کهن‌آباد' },
    { value: 'dibaj', label: 'دیباج' }
  ],

  // استان سیستان و بلوچستان
  sistan_baluchestan: [
    { value: 'zahedan', label: 'زاهدان' },
    { value: 'zabol', label: 'زابل' },
    { value: 'iranshahr', label: 'ایرانشهر' },
    { value: 'chabahar', label: 'چابهار' },
    { value: 'saravan', label: 'سراوان' },
    { value: 'khash', label: 'خاش' },
    { value: 'nikshahr', label: 'نیکشهر' },
    { value: 'sarbaz', label: 'سرباز' },
    { value: 'konarak', label: 'کنارک' },
    { value: 'zehak', label: 'زهک' },
    { value: 'hirmand', label: 'هیرمند' },
    { value: 'qasr_qand', label: 'قصرقند' },
    { value: 'dalgan', label: 'دلگان' },
    { value: 'kalporagan', label: 'کالپوراگان' },
    { value: 'mirabad', label: 'میرآباد' }
  ],

  // استان تهران
  tehran: [
    { value: 'tehran', label: 'تهران' },
    { value: 'varamin', label: 'ورامین' },
    { value: 'eslamshahr', label: 'اسلام‌شهر' },
    { value: 'rey', label: 'ری' },
    { value: 'damavand', label: 'دماوند' },
    { value: 'pakdasht', label: 'پاکدشت' },
    { value: 'robat_karim', label: 'رباط‌کریم' },
    { value: 'shahriyar', label: 'شهریار' },
    { value: 'ferdowsiyeh', label: 'فردوسیه' },
    { value: 'malard', label: 'ملارد' },
    { value: 'qods', label: 'قدس' },
    { value: 'bumehen', label: 'بومهن' },
    { value: 'pishva', label: 'پیشوا' },
    { value: 'firuzkuh', label: 'فیروزکوه' },
    { value: 'shemiran', label: 'شمیران' }
  ],

  // استان یزد
  yazd: [
    { value: 'yazd', label: 'یزد' },
    { value: 'meybod', label: 'میبد' },
    { value: 'ardakan', label: 'اردکان' },
    { value: 'bafq', label: 'بافق' },
    { value: 'taft', label: 'تفت' },
    { value: 'abarkouh', label: 'ابرکوه' },
    { value: 'mehriz', label: 'مهریز' },
    { value: 'khatam', label: 'خاتم' },
    { value: 'ashkezar', label: 'اشکذر' },
    { value: 'zarach', label: 'زرچ' },
    { value: 'hamidiya', label: 'حمیدیا' },
    { value: 'anar', label: 'انار' }
  ],

  // استان زنجان
  zanjan: [
    { value: 'zanjan', label: 'زنجان' },
    { value: 'abhar', label: 'ابهر' },
    { value: 'khoramdareh', label: 'خرمدره' },
    { value: 'qeydar', label: 'قیدار' },
    { value: 'hidaj', label: 'هیدج' },
    { value: 'soltaniyeh', label: 'سلطانیه' },
    { value: 'mahneshan', label: 'ماهنشان' },
    { value: 'ijrud', label: 'ایجرود' },
    { value: 'tarom', label: 'طارم' },
    { value: 'sain_qaleh', label: 'صائین‌قلعه' }
  ]
};