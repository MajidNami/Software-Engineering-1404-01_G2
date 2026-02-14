# Team4 Frontend - API Integration Guide

## 📝 تغییرات انجام شده

فرانت اپلیکیشن حالا به جای داده‌های Mock، از **API واقعی بک‌اند Team4** استفاده میکنه.

## 📁 فایل‌های جدید

### 1. `src/config/api.ts`
تنظیمات API و URLها:
```typescript
BASE_URL: 'http://localhost:8000'
TEAM_PREFIX: '/team4'
ENDPOINTS:
  - /api/facilities/
  - /api/categories/
  - /api/favorites/
  - /api/reviews/
```

### 2. `src/services/placesService.ts`
سرویس اصلی برای ارتباط با API:

#### متدهای موجود:
- **`getFacilities()`**: دریافت لیست تمام مکان‌ها
- **`searchFacilities(filters)`**: جستجو با فیلتر (category, city, province, ...)
- **`getFacilityDetails(id)`**: دریافت جزئیات کامل یک مکان
- **`getFacilityReviews(id)`**: دریافت نظرات یک مکان
- **`getFacilitiesByCategory(category)`**: فیلتر بر اساس دسته‌بندی

## 🔄 تغییرات در `App.tsx`

### State های جدید:
- `allPlaces`: لیست کامل مکان‌ها از API
- `isLoading`: وضعیت بارگذاری

### عملکرد:
1. **بارگذاری اولیه**: با `useEffect` همه facilityها لود میشن
2. **فیلتر دسته‌بندی**: با تغییر category، API جدید call میشه
3. **جزئیات مکان**: با کلیک روی مکان، اطلاعات کامل fetch میشه
4. **Loading State**: اسپینر نشون داده میشه تا داده‌ها بیان

## 🚀 راه‌اندازی

### پیش‌نیازها:
1. بک‌اند Django روی `http://localhost:8000` فعال باشه
2. دیتابیس team4 پر از داده باشه

### اجرا:
```bash
cd team4/front
npm install
npm run dev
```

## 🗺️ نقشه Data Flow

```
User Action
    ↓
App.tsx (Component)
    ↓
placesService.ts (API Call)
    ↓
Django Backend (team4/api/facilities/)
    ↓
Database
    ↓
Response Transform (Backend → Frontend format)
    ↓
Update State & UI
```

## 📊 تبدیل داده‌ها

### Backend → Frontend:
```typescript
Backend Facility {
  fac_id: number
  name_en, name_fa: string
  location: { coordinates: [lng, lat] }
  category: string
  avg_rating: number
  ...
}
    ↓ Transform
Frontend Place {
  id: string
  name: string
  latitude, longitude: number
  category: string
  rating: number
  ...
}
```

## 🔧 تنظیمات

برای تغییر URL بک‌اند:
```typescript
// src/config/api.ts
export const API_CONFIG = {
  BASE_URL: 'http://your-backend-url:8000',
  // ...
};
```

## ⚠️ نکات مهم

1. **CORS**: بک‌اند باید CORS رو برای `localhost:5173` allow کرده باشه
2. **Error Handling**: اگه API fail کنه، آرایه خالی برمیگردونه (بجای crash)
3. **Pagination**: از `page_size: 100` استفاده میکنه (قابل تنظیم)
4. **Routing**: هنوز از mock data استفاده میکنه (طبق درخواست)

## 📝 TODO (نیاز به کار بعدی)

- [ ] اضافه کردن Favorites API integration
- [ ] اضافه کردن Reviews API integration  
- [ ] اضافه کردن Search ب
ا API
- [ ] اضافه کردن Error boundary
- [ ] اضافه کردن Retry mechanism
- [ ] بهبود Loading states

## 🐛 رفع مشکل

### مشکل: API call ها کار نمیکنن
- بررسی کن بک‌اند روشنه: `http://localhost:8000/team4/ping/`
- Console browser رو چک کن برای CORS errors
- Network tab رو بررسی کن

### مشکل: نقشه مکان‌ها رو نشون نمیده
- مطمئن شو `location` field در response هست
- چک کن coordinates به درستی transform شدن (lng, lat → lat, lng)

### مشکل: عکس‌ها نمایش داده نمیشن
- بررسی کن `primary_image` مقدار داره
- URL عکس‌ها accessible باشن

## 📞 پشتیبانی

برای سوالات:
- کدها رو در `src/services/placesService.ts` چک کن
- Logs console browser رو بررسی کن
- Django logs رو ببین
