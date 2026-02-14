# Team 11 - Trip Planning Service

## 🎯 Overview

Team 11's Trip Planning Service is a comprehensive travel planning application that helps users create, manage, and optimize their trip itineraries. The service provides intelligent trip generation, destination recommendations, cost calculations, and collaborative planning features.

## 🏗️ Architecture

The project follows a clean architecture pattern with the following layers:

```
team11/
├── tripPlanService/          # Backend Service (Django + DRF)
│   ├── business/             # Business Logic Layer
│   │   ├── services.py       # Core business services
│   │   ├── generators.py     # Trip generation algorithms
│   │   └── helpers.py        # Helper utilities
│   ├── data/                 # Data Access Layer
│   │   └── models.py         # Django ORM models
│   ├── infrastructure/       # Infrastructure Layer
│   │   └── grpc_clients/     # External service clients
│   ├── presentation/         # Presentation Layer
│   │   ├── views.py          # REST API endpoints
│   │   ├── serializers.py    # Data serializers
│   │   ├── urls.py           # URL routing
│   │   ├── pdf_generator.py  # PDF export functionality
│   │   └── grpc/             # gRPC server
│   └── tripPlanService/      # Django configuration
├── frontend/                 # Frontend Application (React + TypeScript + Vite)
│   ├── src/                  # Source code
│   ├── public/               # Static assets
│   └── dist/                 # Build output
├── docker/                   # Docker setup scripts
├── static/                   # Static files
├── templates/                # Django templates
└── migrations/               # Database migrations
```

## 🚀 Technology Stack

### Backend
- **Framework**: Django 5.2.11 + Django REST Framework 3.15.0
- **Databases**: 
  - PostgreSQL 15 (Relational data)
  - MongoDB 7.0 (NoSQL data)
- **Communication**: gRPC + REST API
- **Task Queue**: Celery + Redis
- **PDF Generation**: WeasyPrint, ReportLab
- **ML Libraries**: NumPy, Pandas, Scikit-learn
- **Authentication**: JWT (PyJWT)

### Frontend
- **Framework**: React 18.2
- **Language**: TypeScript 5.9
- **Build Tool**: Vite 7.3
- **Routing**: React Router 7.13
- **HTTP Client**: Axios 1.13
- **UI**: TailwindCSS 4.1, Radix UI
- **Date Handling**: Jalaali (Persian calendar)

### Infrastructure
- **Container**: Docker + Docker Compose
- **Gateway**: NGINX
- **Platform**: Linux/AMD64

## 📋 Prerequisites

Before running the project, ensure you have the following installed:

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Git

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Software-Engineering-1404-01_G2_Team11
```

### 2. Environment Configuration

Create a `.env` file in the `team11/` directory (or modify the existing one):

```env
# PostgreSQL Settings
TEAM11_POSTGRES_DB=team11_db
TEAM11_POSTGRES_USER=team11_user
TEAM11_POSTGRES_PASSWORD=your_secure_password
TEAM11_POSTGRES_PORT=5432
TEAM11_POSTGRES_HOST=team11_postgres

# MongoDB Settings
TEAM11_MONGO_DB=team11_nosql
TEAM11_MONGO_USER=team11_mongo
TEAM11_MONGO_PASSWORD=your_secure_mongo_password
TEAM11_MONGO_PORT=27017
TEAM11_MONGO_HOST=team11_mongo

# Connection URLs
TEAM11_DATABASE_URL=postgresql://team11_user:your_secure_password@team11_postgres:5432/team11_db
TEAM11_MONGO_URL=mongodb://team11_mongo:your_secure_mongo_password@team11_mongo:27017/team11_nosql?authSource=admin

# JWT Secret (must match core project)
JWT_SECRET=your_jwt_secret_key

# Service URLs
TRIP_PLAN_GRPC_URL=trip-plan-gateway
TRIP_PLAN_REST_URL=trip-plan-gateway/front
TEAM_PORT=9151
```

### 3. Running the Application

#### Option A: Run All Services (Recommended)

From the project root:

```bash
bash ./linux_scripts/up-all.sh
```

#### Option B: Run Team 11 Services Only

```bash
cd team11
docker compose up -d --build
```

#### Option C: Run Individual Services

```bash
# Navigate to team11 directory
cd team11

# Start databases
docker compose up -d team11_postgres team11_mongo

# Start backend service
docker compose up -d --build trip-plan

# Start frontend
docker compose up -d --build vite-app

# Start gateway
docker compose up -d trip-plan-gateway
```

### 4. Verify Installation

Check if all services are running:

```bash
docker compose ps
```

Expected services:
- `trip-plan` (Backend API)
- `vite-app` (Frontend)
- `trip-plan-gateway` (NGINX Gateway)
- `team11_postgres` (PostgreSQL Database)
- `team11_mongo` (MongoDB Database)

### 5. Access the Application

- **Frontend Application**: http://localhost:9151/team11/
- **Backend API**: http://localhost:9151/api/
- **Django Admin**: http://localhost:9151/api/admin/
- **Health Check**: http://localhost:9151/api/ping/

## 📡 API Documentation

### Base URL

```
http://localhost:9151/api/
```

### Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### API Endpoints

#### 🔍 Health & Testing

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/test/` | Test endpoint for development | No |
| GET | `/ping/` | Health check | Yes |
| GET | `/trip-plan/trips` | OK status check | No |

#### 🗺️ Trip Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/trips/` | List all trips | Optional* |
| GET | `/trips/{id}/` | Get trip details | No |
| POST | `/trips/` | Create a new trip | Optional* |
| PUT | `/trips/{id}/` | Update trip (full) | Yes |
| PATCH | `/trips/{id}/` | Update trip (partial) | Yes |
| DELETE | `/trips/{id}/` | Delete trip | Yes |

*Auth is optional but filters results based on user

**Create Trip Request Body:**
```json
{
  "title": "سفر اصفهان",
  "province": "اصفهان",
  "city": "اصفهان",
  "start_date": "2026-03-15",
  "end_date": "2026-03-17",
  "budget_level": "MEDIUM",
  "travel_style": "COUPLE",
  "daily_available_hours": 12,
  "interests": ["تاریخی", "فرهنگی"]
}
```

**Budget Levels:** `ECONOMY`, `MEDIUM`, `LUXURY`, `UNLIMITED`

**Travel Styles:** `SOLO`, `COUPLE`, `FAMILY`, `FRIENDS`, `BUSINESS`

#### 🤖 AI-Powered Trip Generation

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/trips/generate/` | Generate trip automatically | Optional |

**Request Body:**
```json
{
  "province": "اصفهان",
  "city": "اصفهان",
  "start_date": "2026-03-15",
  "end_date": "2026-03-17",
  "interests": ["تاریخی", "فرهنگی"],
  "budget_level": "MEDIUM",
  "daily_available_hours": 12,
  "travel_style": "COUPLE",
  "user_id": 123
}
```

#### 🌍 Destination Suggestions

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/destinations/suggest/` | Get destination recommendations | No |

**Request Body:**
```json
{
  "season": "spring",
  "budget_level": "MEDIUM",
  "travel_style": "COUPLE",
  "interests": ["تاریخی", "طبیعت"]
}
```

**Seasons:** `spring`, `summer`, `fall`, `winter`

**Response:**
```json
{
  "suggestions": [
    {
      "city": "اصفهان",
      "province": "اصفهان",
      "score": 95,
      "reason": "بهترین شهر برای علاقه‌مندان به تاریخ و فرهنگ",
      "highlights": ["میدان نقش جهان", "سی‌وسه‌پل"],
      "best_season": "spring",
      "estimated_cost": "2500000",
      "duration_days": 3,
      "description": "اصفهان با آب و هوای معتدل در بهار...",
      "images": ["url1", "url2"]
    }
  ]
}
```

#### 📅 Trip Days Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/trip-days/` | List all trip days | No |
| GET | `/trip-days/{id}/` | Get day details | No |
| POST | `/trip-days/` | Create a day | Yes |
| PUT | `/trip-days/{id}/` | Update day | Yes |
| DELETE | `/trip-days/{id}/` | Delete day | Yes |
| POST | `/trips/{id}/days/` | Add day to trip | Yes |

#### 📝 Trip Items Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/items/` | List all items | No |
| GET | `/items/{id}/` | Get item details | No |
| POST | `/items/` | Create an item | Yes |
| PUT | `/items/{id}/` | Update item | Yes |
| DELETE | `/items/{id}/` | Delete item | Yes |
| POST | `/days/{day_id}/items/bulk/` | Bulk create items for a day | Yes |

**Item Request Body:**
```json
{
  "trip_day": 1,
  "facility_id": 123,
  "item_type": "VISIT",
  "start_time": "09:00:00",
  "end_time": "11:00:00",
  "notes": "Visit in the morning"
}
```

**Item Types:** `VISIT`, `STAY`

#### 🔄 Alternative Recommendations

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/items/{id}/alternatives/` | Get alternative items | No |

**Response:**
```json
{
  "original": {
    "id": 1,
    "facility_name": "Naqsh-e Jahan Square"
  },
  "alternatives": [
    {
      "facility_id": 456,
      "facility_name": "Si-o-se-pol Bridge",
      "score": 0.85,
      "reason": "Similar historical significance"
    }
  ]
}
```

#### 💰 Cost Calculation

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/trips/{trip_id}/cost/` | Get trip cost breakdown | No |

**Response:**
```json
{
  "trip_id": 1,
  "total_cost": 5000000,
  "currency": "IRR",
  "breakdown": {
    "accommodation": 2000000,
    "transportation": 1000000,
    "activities": 1500000,
    "food": 500000
  }
}
```

#### 👤 Guest Conversion

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/trips/{id}/claim/` | Claim guest trip as user | Yes |

Converts an anonymous guest trip to a user-owned trip.

#### 📄 PDF Export

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/trips/{id}/export-pdf/` | Export trip as PDF | No |

Downloads a formatted PDF document of the trip itinerary.

#### 🔗 Sharing & Collaboration

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/trips/{id}/share/` | Create shareable link | Yes |
| GET | `/trips/{id}/collaborators/` | List collaborators | Yes |

#### ⭐ Reviews

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/trips/{id}/review/` | Add review to trip | Yes |
| GET | `/trips/{id}/reviews/` | Get trip reviews | No |

### Query Parameters

#### List Trips
```
GET /trips/?user_id=123&status=ACTIVE&page=1
```

- `user_id`: Filter by user
- `status`: Filter by status (`DRAFT`, `ACTIVE`, `FINALIZED`, `COMPLETED`)
- `page`: Pagination

## 🗄️ Database Schema

### PostgreSQL (Relational Data)

#### Trip
- `trip_id` (BigAutoField, PK)
- `user_id` (CharField, nullable)
- `title` (CharField)
- `province` (CharField)
- `city` (CharField, nullable)
- `start_date` (DateField)
- `end_date` (DateField, nullable)
- `duration_days` (IntegerField)
- `budget_level` (CharField) - ECONOMY/MEDIUM/LUXURY/UNLIMITED
- `travel_style` (CharField) - SOLO/COUPLE/FAMILY/FRIENDS/BUSINESS
- `daily_available_hours` (IntegerField)
- `status` (CharField) - DRAFT/ACTIVE/FINALIZED/COMPLETED
- `copied_from_trip` (ForeignKey, self-reference)

#### TripDay
- `day_id` (BigAutoField, PK)
- `trip` (ForeignKey to Trip)
- `day_number` (IntegerField)
- `date` (DateField)
- `notes` (TextField)

#### TripItem
- `item_id` (BigAutoField, PK)
- `trip_day` (ForeignKey to TripDay)
- `facility_id` (IntegerField) - Reference to external Facility service
- `item_type` (CharField) - VISIT/STAY
- `start_time` (TimeField)
- `end_time` (TimeField)
- `order_index` (IntegerField)
- `notes` (TextField)

### MongoDB (NoSQL Data)

Used for storing flexible data like:
- User preferences
- Search history
- Analytics data
- Cached recommendations

## 🧪 Testing

### Run Backend Tests

```bash
cd team11/tripPlanService
python manage.py test
```

### Run Frontend Tests

```bash
cd team11/frontend
npm test
```

## 🔧 Development

### Backend Development

```bash
# Navigate to tripPlanService
cd team11/tripPlanService

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver 0.0.0.0:2004
```

### Frontend Development

```bash
# Navigate to frontend
cd team11/frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### gRPC Server

The gRPC server runs automatically with the Docker container. For manual start:

```bash
cd team11/tripPlanService
python presentation/grpc/server/grpc_server.py
```

## 📦 Port Configuration

| Service | Port | Description |
|---------|------|-------------|
| Gateway | 9151 | Main entry point (NGINX) |
| Frontend Dev | 3000 | Vite development server |
| Backend API | 2004 | Django REST API |
| gRPC Server | 50051 | gRPC communication |
| PostgreSQL | 5433 | PostgreSQL database (external) |
| MongoDB | 27018 | MongoDB database (external) |

## 🛑 Stopping the Application

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes data)
docker compose down -v

# Stop specific service
docker compose stop trip-plan
```

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check database health
docker compose ps

# View database logs
docker compose logs team11_postgres
docker compose logs team11_mongo

# Restart databases
docker compose restart team11_postgres team11_mongo
```

### Backend Service Issues

```bash
# View backend logs
docker compose logs trip-plan

# Rebuild backend
docker compose up -d --build trip-plan

# Access backend container
docker compose exec trip-plan bash
```

### Frontend Issues

```bash
# View frontend logs
docker compose logs vite-app

# Rebuild frontend
docker compose up -d --build vite-app
```

### Network Issues

```bash
# Ensure app404_net network exists
docker network ls | grep app404

# Create network if missing
docker network create app404_net
```

## 📚 Additional Resources

### Related Documentation
- [Frontend README](frontend/README.md) - Frontend-specific documentation
- [API Integration Guide](frontend/API_INTEGRATION_README.md) - Frontend-Backend integration

### External Dependencies
- **Facility Service** (Team 10): Provides location and facility data
- **Recommendation Service** (Team 10): AI-powered recommendations
- **Wiki Service** (Team 10): City descriptions and images
- **Core Service**: User authentication and management

## 👥 Team Members

Team 11 - Software Engineering Course 1404-01

**Last Updated**: February 2026
