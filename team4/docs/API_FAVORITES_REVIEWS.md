# 📚 API Documentation - Favorites, Reviews & Emergency Features

## Overview
این مستند شامل API های جدید برای **علاقه‌مندی‌ها**، **نظرات** و **امکانات اضطراری** است که به تیم 4 اضافه شده است.

---

## 🔖 Favorites (علاقه‌مندی‌ها)

### Base URL
```
/team4/api/favorites/
```

### 1. لیست علاقه‌مندی‌های کاربر
```http
GET /team4/api/favorites/
```

**Response:**
```json
{
  "count": 10,
  "next": "...",
  "previous": null,
  "results": [
    {
      "favorite_id": 1,
      "user": "uuid",
      "user_email": "user@example.com",
      "facility": 123,
      "facility_detail": {
        "fac_id": 123,
        "name_fa": "هتل آزادی",
        "name_en": "Azadi Hotel",
        "category": {...},
        "city": {...},
        "location": {...},
        "avg_rating": 4.5,
        "review_count": 120,
        "primary_image": "https://...",
        "price_from": 1500000.00,
        "is_24_hour": true
      },
      "created_at": "2026-02-09T12:00:00Z"
    }
  ]
}
```

---

### 2. افزودن به علاقه‌مندی‌ها
```http
POST /team4/api/favorites/
```

**Request Body:**
```json
{
  "facility": 123
}
```

**Response (201):**
```json
{
  "message": "مکان با موفقیت به علاقه‌مندی‌ها اضافه شد",
  "data": {
    "favorite_id": 1,
    "user": "uuid",
    "user_email": "user@example.com",
    "facility": 123,
    "facility_detail": {...},
    "created_at": "2026-02-09T12:00:00Z"
  }
}
```

**Error (400):**
```json
{
  "detail": "این مکان قبلاً به علاقه‌مندی‌های شما اضافه شده است."
}
```

---

### 3. حذف از علاقه‌مندی‌ها
```http
DELETE /team4/api/favorites/{favorite_id}/
```

**Response (200):**
```json
{
  "message": "مکان از علاقه‌مندی‌ها حذف شد"
}
```

---

### 4. Toggle علاقه‌مندی (افزودن/حذف یکجا)
```http
POST /team4/api/favorites/toggle/
```

**Request Body:**
```json
{
  "facility": 123
}
```

**Response - افزودن (201):**
```json
{
  "message": "added",
  "is_favorite": true
}
```

**Response - حذف (200):**
```json
{
  "message": "removed",
  "is_favorite": false
}
```

---

### 5. بررسی وضعیت علاقه‌مندی
```http
GET /team4/api/favorites/check/?facility=123
```

**Response:**
```json
{
  "is_favorite": true,
  "facility_id": "123"
}
```

---

## ⭐ Reviews (نظرات)

### Base URL
```
/team4/api/reviews/
```

### 1. لیست نظرات
```http
GET /team4/api/reviews/
```

**Query Parameters:**
- `facility`: فیلتر بر اساس مکان (مثال: `?facility=123`)
- `user_only`: فقط نظرات کاربر جاری (مثال: `?user_only=true`)
- `rating`: فیلتر بر اساس امتیاز (مثال: `?rating=5`)

**Response:**
```json
{
  "count": 50,
  "next": "...",
  "previous": null,
  "results": [
    {
      "review_id": 1,
      "user": "uuid",
      "user_email": "user@example.com",
      "user_name": "احمد محمدی",
      "facility": 123,
      "facility_name": "هتل آزادی",
      "rating": 5,
      "comment": "هتل بسیار عالی با خدمات درجه یک",
      "is_approved": true,
      "created_at": "2026-02-09T12:00:00Z",
      "updated_at": "2026-02-09T12:00:00Z"
    }
  ]
}
```

---

### 2. ثبت نظر جدید
```http
POST /team4/api/reviews/
```

**Request Body:**
```json
{
  "facility": 123,
  "rating": 5,
  "comment": "هتل بسیار عالی با خدمات درجه یک"
}
```

**Response (201):**
```json
{
  "message": "نظر شما با موفقیت ثبت شد",
  "data": {
    "review_id": 1,
    "user": "uuid",
    "user_email": "user@example.com",
    "user_name": "احمد محمدی",
    "facility": 123,
    "facility_name": "هتل آزادی",
    "rating": 5,
    "comment": "هتل بسیار عالی با خدمات درجه یک",
    "is_approved": true,
    "created_at": "2026-02-09T12:00:00Z",
    "updated_at": "2026-02-09T12:00:00Z"
  }
}
```

**Error (400):**
```json
{
  "detail": "شما قبلاً برای این مکان نظر ثبت کرده‌اید. می‌توانید نظر خود را ویرایش کنید."
}
```

---

### 3. ویرایش نظر
```http
PUT /team4/api/reviews/{review_id}/
PATCH /team4/api/reviews/{review_id}/
```

**Request Body (PATCH):**
```json
{
  "rating": 4,
  "comment": "نظر به‌روزرسانی شده"
}
```

**Response (200):**
```json
{
  "message": "نظر با موفقیت ویرایش شد",
  "data": {
    "review_id": 1,
    "rating": 4,
    "comment": "نظر به‌روزرسانی شده",
    ...
  }
}
```

**Note:** فقط صاحب نظر یا ادمین می‌تواند نظر را ویرایش کند.

---

### 4. حذف نظر
```http
DELETE /team4/api/reviews/{review_id}/
```

**Response (200):**
```json
{
  "message": "نظر با موفقیت حذف شد"
}
```

**Note:** فقط صاحب نظر یا ادمین می‌تواند نظر را حذف کند.

---

### 5. دریافت نظرات یک مکان
```http
GET /team4/api/facilities/{facility_id}/reviews/
```

**Query Parameters:**
- `rating`: فیلتر بر اساس امتیاز (مثال: `?rating=5`)

**Response:**
```json
{
  "count": 25,
  "next": "...",
  "previous": null,
  "results": [
    {
      "review_id": 1,
      "user_email": "user@example.com",
      "user_name": "احمد محمدی",
      "rating": 5,
      "comment": "هتل بسیار عالی",
      "created_at": "2026-02-09T12:00:00Z"
    }
  ]
}
```

---

## 🚨 Emergency Facilities (امکانات اضطراری)

### دریافت لیست امکانات اضطراری
```http
GET /team4/api/facilities/emergency/
```

**Query Parameters:**
- `city`: نام شهر (اختیاری)
- `lat`: عرض جغرافیایی (اختیاری)
- `lng`: طول جغرافیایی (اختیاری)
- `radius`: شعاع جستجو به کیلومتر (پیش‌فرض: 10)

**مثال 1: بدون موقعیت جغرافیایی**
```http
GET /team4/api/facilities/emergency/?city=تهران
```

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "fac_id": 1,
      "name_fa": "بیمارستان امام خمینی",
      "name_en": "Imam Khomeini Hospital",
      "category": {
        "category_id": 1,
        "name_fa": "بیمارستان",
        "name_en": "Hospital",
        "is_emergency": true,
        "marker_color": "red"
      },
      "city": {...},
      "location": {...},
      "avg_rating": 4.2,
      "review_count": 85,
      "is_24_hour": true
    }
  ]
}
```

**مثال 2: با موقعیت جغرافیایی**
```http
GET /team4/api/facilities/emergency/?lat=35.6892&lng=51.3890&radius=5
```

**Response:**
```json
{
  "count": 8,
  "results": [
    {
      "fac_id": 1,
      "name_fa": "بیمارستان امام خمینی",
      "distance_km": 1.2,
      "category": {
        "is_emergency": true
      },
      ...
    },
    {
      "fac_id": 2,
      "name_fa": "اورژانس 115",
      "distance_km": 2.5,
      ...
    }
  ]
}
```

**توضیحات:**
- امکانات بر اساس فاصله از موقعیت کاربر مرتب می‌شوند (نزدیک‌ترین ابتدا)
- فقط امکاناتی که `category.is_emergency = true` دارند نمایش داده می‌شوند
- امکانات 24 ساعته با `is_24_hour: true` مشخص می‌شوند

---

## 🔐 Authentication

**همه API های favorites و reviews نیاز به احراز هویت دارند.**

از هدر زیر استفاده کنید:
```http
Authorization: Bearer <access_token>
```

یا از دکوراتور `@api_login_required` در views استفاده شده است.

---

## 📊 Models Schema

### Favorite Model
```python
class Favorite:
    favorite_id: BigAutoField (PK)
    user: ForeignKey(User)
    facility: ForeignKey(Facility)
    created_at: DateTimeField
```

### Review Model
```python
class Review:
    review_id: BigAutoField (PK)
    user: ForeignKey(User)
    facility: ForeignKey(Facility)
    rating: IntegerField (1-5)
    comment: TextField
    is_approved: BooleanField
    created_at: DateTimeField
    updated_at: DateTimeField
```

**Constraints:**
- هر کاربر فقط یک بار می‌تواند یک مکان را به علاقه‌مندی‌ها اضافه کند
- هر کاربر فقط یک بار می‌تواند برای یک مکان نظر ثبت کند

---

## 🎯 Features

### ✅ Favorites
- [x] افزودن مکان به علاقه‌مندی‌ها
- [x] حذف مکان از علاقه‌مندی‌ها
- [x] نمایش لیست علاقه‌مندی‌ها
- [x] Toggle علاقه‌مندی (افزودن/حذف یکجا)
- [x] بررسی وضعیت علاقه‌مندی یک مکان
- [x] جلوگیری از افزودن تکراری
- [x] Pagination

### ✅ Reviews
- [x] ثبت نظر و امتیاز
- [x] ویرایش نظر
- [x] حذف نظر
- [x] نمایش نظرات یک مکان
- [x] فیلتر بر اساس امتیاز
- [x] بروزرسانی خودکار avg_rating و review_count
- [x] تایید نظرات توسط ادمین
- [x] جلوگیری از ثبت نظر تکراری
- [x] Pagination

### ✅ Emergency
- [x] فیلتر امکانات اضطراری
- [x] جستجو بر اساس شهر
- [x] جستجو بر اساس موقعیت جغرافیایی
- [x] محاسبه فاصله از کاربر
- [x] مرتب‌سازی بر اساس فاصله
- [x] نمایش امکانات 24 ساعته

---

## 🔄 Auto-Update avg_rating

هنگام ثبت، ویرایش یا حذف نظر، فیلدهای `avg_rating` و `review_count` در مدل Facility به‌صورت خودکار به‌روزرسانی می‌شوند.

```python
# در Review.save() و Review.delete()
self.update_facility_rating()
```

این کار در Django signals یا در متدهای save/delete مدل Review انجام می‌شود.

---

## 📝 Notes

1. **Pagination:** همه endpoint های لیست از pagination پشتیبانی می‌کنند (10 آیتم در هر صفحه)
2. **Permissions:** endpoints favorites و reviews نیاز به احراز هویت دارند
3. **Validation:** امتیازات باید بین 1 تا 5 باشند
4. **Unique Constraints:** هر کاربر فقط یک بار می‌تواند برای یک مکان نظر بدهد یا آن را به علاقه‌مندی‌ها اضافه کند
5. **Emergency Categories:** برای مشخص کردن یک دسته‌بندی به عنوان اضطراری، در Django Admin فیلد `is_emergency` را true کنید

---

## 🚀 Testing

### Test Favorites API
```bash
# افزودن به علاقه‌مندی‌ها
curl -X POST http://localhost:8000/team4/api/favorites/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"facility": 123}'

# لیست علاقه‌مندی‌ها
curl -X GET http://localhost:8000/team4/api/favorites/ \
  -H "Authorization: Bearer <token>"

# Toggle
curl -X POST http://localhost:8000/team4/api/favorites/toggle/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"facility": 123}'
```

### Test Reviews API
```bash
# ثبت نظر
curl -X POST http://localhost:8000/team4/api/reviews/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"facility": 123, "rating": 5, "comment": "عالی بود"}'

# نظرات یک مکان
curl -X GET http://localhost:8000/team4/api/facilities/123/reviews/
```

### Test Emergency API
```bash
# امکانات اضطراری در تهران
curl -X GET "http://localhost:8000/team4/api/facilities/emergency/?city=تهران"

# امکانات اضطراری در شعاع 5 کیلومتری
curl -X GET "http://localhost:8000/team4/api/facilities/emergency/?lat=35.6892&lng=51.3890&radius=5"
```

---

## 📧 Contact & Support

برای سوالات و مشکلات با تیم توسعه تماس بگیرید.
