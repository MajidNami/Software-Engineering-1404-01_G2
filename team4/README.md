# Team 4 - Facilities & Transportation Service

Facility management service (hotels, restaurants, hospitals, pharmacies, clinics, museums, shopping centers) and transportation services.

## 📋 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install mysqlclient  # For MySQL
```

### 2. Database Configuration

**a) Create Database in MySQL:**

```sql
CREATE DATABASE IF NOT EXISTS team4_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**b) Configure `.env` File:**

Add this line to the `.env` file in the project root:

```env
TEAM4_DATABASE_URL=mysql://root:YOUR_MYSQL_PASSWORD@localhost:3306/team4_db
```

### 3. Django Configuration

Ensure `team4` is added to `INSTALLED_APPS`:

```python
# app404/settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'django_filters',
    'team4',
]
```

### 4. Migrations

```bash
python manage.py makemigrations team4
python manage.py migrate --database=team4
```

### 5. Load Initial Data

```bash
python manage.py loaddata team4/fixtures/provinces.json --database=team4
python -m team4.load_cities  # Cities via Python script
python manage.py loaddata team4/fixtures/categories.json --database=team4
python manage.py loaddata team4/fixtures/amenities.json --database=team4
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

---

## 🔌 API Endpoints

### Facilities

#### 1. List Facilities with Search and Filters
```http
GET /team4/api/facilities/

Query Parameters:
- city: City name (example: Tehran)
- category: Category name (example: Hotel)
- min_price: Minimum price
- max_price: Maximum price
- min_rating: Minimum rating (1-5)
- amenities: List of amenity_id (comma-separated, example: 1,2,5)
- is_24_hour: Filter 24-hour facilities (true/false)
- sort: Sort type (distance|rating|review_count)
- page: Page number
- page_size: Items per page (default: 10)
```

**Example:**
```bash
curl "http://localhost:8000/team4/api/facilities/?city=Tehran&category=Hotel&min_rating=4&sort=rating"
```

#### 2. Facility Details
```http
GET /team4/api/facilities/{fac_id}/
```

**Example:**
```bash
curl "http://localhost:8000/team4/api/facilities/1/"
```

#### 3. Nearby Facilities
```http
GET /team4/api/facilities/{fac_id}/nearby/

Query Parameters:
- radius: Search radius (km, default: 5)
- category: Category filter (optional)
```

**Example:**
```bash
curl "http://localhost:8000/team4/api/facilities/1/nearby/?radius=5&category=Restaurant"
```

#### 4. Compare Hotels
```http
POST /team4/api/facilities/compare/

Body (JSON):
{
  "facility_ids": [1, 2, 3]
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/team4/api/facilities/compare/" \
  -H "Content-Type: application/json" \
  -d '{"facility_ids": [1, 2]}'
```

---

### Categories

```http
GET /team4/api/categories/
GET /team4/api/categories/{id}/
```

**Available Categories:**
- Hotels
- Restaurants
- Hospitals
- Shopping Centers
- Museums
- Cafes
- Pharmacies
- Clinics

---

### Region Search

```http
GET /team4/api/regions/search/

Query Parameters:
- query: Search query (required)
- region_type: Filter by type - 'province', 'city', or 'village' (optional)
```

**Example:**
```bash
curl "http://localhost:8000/team4/api/regions/search/?query=Tehran"
```

---

### Favorites

#### 1. List User Favorites
```http
GET /team4/api/favorites/
```

#### 2. Add to Favorites
```http
POST /team4/api/favorites/?facility={facility_id}
```

#### 3. Toggle Favorite Status
```http
POST /team4/api/favorites/toggle/

Body (JSON):
{
  "facility": 123
}
```

#### 4. Check if Favorited
```http
GET /team4/api/favorites/check/?facility={facility_id}
```

#### 5. Remove from Favorites
```http
DELETE /team4/api/favorites/{favorite_id}/
```

---

### Reviews

#### 1. List Reviews
```http
GET /team4/api/reviews/

Query Parameters:
- facility: Filter by facility ID
- min_rating: Minimum rating filter
```

#### 2. Create Review
```http
POST /team4/api/reviews/

Body (JSON):
{
  "facility": 123,
  "rating": 5,
  "comment": "Excellent service!"
}
```

#### 3. Update Review
```http
PUT /team4/api/reviews/{review_id}/
PATCH /team4/api/reviews/{review_id}/
```

#### 4. Delete Review
```http
DELETE /team4/api/reviews/{review_id}/
```

---

### Routing & Navigation

```http
POST /team4/api/routing/

Body (JSON):
{
  "type": "car",
  "origin": {
    "latitude": 35.7219,
    "longitude": 51.3347
  },
  "destination": {
    "latitude": 35.6892,
    "longitude": 51.3890
  },
  "avoidTrafficZone": false,
  "avoidOddEvenZone": false,
  "alternative": false
}
```

**Vehicle Types:**
- `car`: Automobile
- `motorcycle`: Motorcycle

---

## 🔐 Authentication

Most endpoints require authentication. The API uses JWT tokens stored in HttpOnly cookies.

**Login:**
```http
POST /team4/login/

Body (JSON):
{
  "username": "your_username",
  "password": "your_password"
}
```

**Register:**
```http
POST /team4/register/

Body (JSON):
{
  "username": "new_user",
  "password": "secure_password",
  "email": "user@example.com"
}
```

**Logout:**
```http
POST /team4/logout/
```

---

## 🧪 Running Tests

### Test All Models and Services
```bash
python manage.py test team4
```

### Test Models Only
```bash
python manage.py test team4.tests.test_models
```

### Test Services Only
```bash
python manage.py test team4.tests.test_services
```

### Test with Coverage
```bash
pip install coverage
coverage run --source='team4' manage.py test team4
coverage report
coverage html
```

---

## 📊 Django Admin Panel

Access the admin panel at:
```
http://localhost:8000/admin/
```

You can manage:
- Provinces and Cities
- Categories
- Amenities
- Facilities
- Prices
- Images
- Reviews
- Favorites

---

## 🎨 Frontend Development

### Build Frontend
```bash
cd team4/front
npm install
npm run build
```

The build process automatically copies the compiled assets to Django's static and template directories.

### Development Mode
```bash
cd team4/front
npm run dev
```

### Frontend Structure
```
team4/front/
├── src/
│   ├── components/       # React components
│   ├── services/         # API service layer
│   ├── utils/            # Utility functions
│   ├── data/             # Mock data and types
│   └── config/           # Configuration files
├── static/               # Built assets
└── templates/            # Django templates
```

---

## 📁 Project Structure

```
team4/
├── models.py              # 8 Models
├── serializers.py         # Serializers (cleaned, no Swagger decorators)
├── views.py               # ViewSets (cleaned, no Swagger decorators)
├── urls.py                # URL Routing
├── admin.py               # Django Admin Configuration
├── auth.py                # Authentication views
├── services/
│   ├── __init__.py
│   ├── facility_service.py
│   └── region_service.py
├── fixtures/              # Initial data
│   ├── provinces.json
│   ├── cities.json
│   ├── categories.json
│   └── amenities.json
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── front/                 # React + TypeScript frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── static/                # Django static files
├── templates/             # Django templates
└── README.md
```

---

## ✅ Implementation Checklist

- ✅ Models (8 tables with proper relationships)
- ✅ Migrations
- ✅ Services (Business Logic layer)
- ✅ Serializers (8 Serializers, cleaned from Swagger decorators)
- ✅ ViewSets (API endpoints, cleaned from Swagger decorators)
- ✅ URLs (RESTful routing)
- ✅ Django Admin (Full management interface)
- ✅ Fixtures (Initial seed data)
- ✅ Tests (Models + Services)
- ✅ Authentication (JWT with HttpOnly cookies)
- ✅ Frontend (React + TypeScript + Vite)
- ✅ API Integration (Neshan Maps integration)
- ✅ Documentation

---

## 🚀 Next Steps

1. **Test APIs with Postman/Thunder Client**
2. **Add more data through Django Admin**
3. **Frontend deployment optimization**
4. **Integration with other team services**
5. **Performance optimization and caching**

---

## 📝 Important Notes

- All Swagger/drf_spectacular decorators have been removed from the codebase
- Authentication uses HttpOnly cookies for security
- All fetch requests include `credentials: 'include'` for cookie handling
- Frontend build automatically syncs with Django templates
- Categories updated to match project requirements:
  - Hotels (هتل)
  - Restaurants (رستوران)
  - Hospitals (بیمارستان)
  - Shopping Centers (مرکز خرید)
  - Museums (موزه)
  - Cafes (کافه)
  - Pharmacies (داروخانه)
  - Clinics (درمانگاه)

---

## 📞 Team Contact

**Team 4 - Facilities & Transportation**
- Backend Core: Developer 1 ✅
- Services & Integration: Developer 2
- APIs & ViewSets: Developer 3
- Frontend: Developer 4

