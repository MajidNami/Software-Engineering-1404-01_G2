export const TRAVEL_SEASONS = [
  { value: 'SPRING', label: 'بهار' },
  { value: 'SUMMER', label: 'تابستان' },
  { value: 'AUTUMN', label: 'پاییز' },
  { value: 'WINTER', label: 'زمستان' }
];

export const GEOGRAPHIC_REGIONS = [
  { value: 'NORTH', label: 'شمال' },
  { value: 'SOUTH', label: 'جنوب' },
  { value: 'EAST', label: 'شرق' },
  { value: 'WEST', label: 'غرب' },
  { value: 'CENTRAL', label: 'مرکز' }
];

export const BUDGET_LEVELS = [
  { value: 'ECONOMY', label: 'اقتصادی' },
  { value: 'MEDIUM', label: 'معمولى' },
  { value: 'LUXURY', label: 'لوکس' },
  { value: 'UNLIMITED', label: 'بدون محدودیت' }
];

export const TRAVEL_STYLES = [
  { value: 'SOLO', label: 'انفرادی' },
  { value: 'COUPLE', label: 'دونفره' },
  { value: 'FAMILY', label: 'خانوادگی' },
  { value: 'FRIENDS', label: 'دوستانه' },
  { value: 'BUSINESS', label: 'کاری' }
];

export const INITIAL_INTERESTS = [  
  { value: 'HISTORICAL', label: 'تاریخی' },
  { value: 'RECREATIONAL' , label: 'تفریحی'},
  { value: 'RELIGIOUS', label: 'مذهبی و زیارتی' },
  { value: 'ART_CULTURE', label: 'فرهنگ و هنر' },
  { value: 'SHOPPING', label: 'بازار و خرید' },
  { value: 'NATURAL', label: 'طبیعت‌گردی' },
  { value: 'DINING', label: 'غذا و خوراک' },
  { value: 'STUDY', label: 'آموزشی' },
  { value: 'EVENTS', label: 'رویداد‌ و جشنواره' }
];

export const PROGRAM_DENSITY = [
  { value: 'RELAXED', label: 'کم‌تراکم (آرام)' },
  { value: 'BALANCED', label: 'متوسط (برنامه‌ریزی شده)' },
  { value: 'INTENSIVE', label: 'پرتراکم (فشرده)' }
]

const createLookup = (arr: { value: string; label: string }[]) =>
  Object.fromEntries(arr.map(item => [item.value, item.label]));

// Create maps
export const TRAVEL_SEASONS_MAP = createLookup(TRAVEL_SEASONS);
export const GEOGRAPHIC_REGIONS_MAP = createLookup(GEOGRAPHIC_REGIONS);
export const BUDGET_LEVELS_MAP = createLookup(BUDGET_LEVELS);
export const TRAVEL_STYLES_MAP = createLookup(TRAVEL_STYLES);
export const INITIAL_INTERESTS_MAP = createLookup(INITIAL_INTERESTS);
export const PROGRAM_DENSITY_MAP = createLookup(PROGRAM_DENSITY);