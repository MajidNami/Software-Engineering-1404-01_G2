# Team 8 Backend — Tourism Comment & Rating System

Django REST API for a tourism platform where users can post comments (with optional media), write replies, rate places, vote on posts, and report content.

## Stack

- **Django 4.2** + Django REST Framework
- **PostgreSQL + PostGIS** (geospatial queries)
- **MinIO** (S3-compatible media storage)
- **JWT** authentication (bcrypt + PyJWT)

## Quick Start

```bash
# 1. Start dependencies (postgres + minio)
cd team8
docker compose -f docker-compose.dev-db.yml up -d

# 2. Create venv & install
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Init database
bash reset_db.sh

# 4. Run
python manage.py runserver 0.0.0.0:8001
```

## Environment

Configured via `.env` (see `.env.local` for defaults):

| Variable | Default |
|---|---|
| `TEAM8_DATABASE_URL` | `postgresql://team8_user:team8_pass@localhost:5432/team8_db` |
| `S3_ENDPOINT_URL` | `http://localhost:9000` |
| `S3_ACCESS_KEY` | `minioadmin` |
| `S3_SECRET_KEY` | `minioadmin123` |
| `S3_BUCKET_NAME` | `team8-media` |

## Authentication

Standalone JWT auth via httpOnly cookie (`access_token`) or `Authorization: Bearer <token>` header.

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register/` | POST | Register (username, email, password) |
| `/api/auth/login/` | POST | Login (username, password) |
| `/api/auth/logout/` | POST | Clear cookie |
| `/api/auth/verify/` | GET | Validate current token |
| `/api/auth/profile/` | GET | Current user info |

## API Endpoints

All under `/api/`. Paginated (20/page). Supports `?page=N`.

### Reference Data (public, read-only)

| Endpoint | Description |
|---|---|
| `GET /api/provinces/` | 31 Iranian provinces |
| `GET /api/cities/?province=ID` | Cities, filterable by province |
| `GET /api/categories/` | Place categories |

### Places (public read, auth write)

| Endpoint | Description |
|---|---|
| `GET /api/places/` | List (filter: `category`, `city`, `city__province`; search: `title`, `description`) |
| `GET /api/places/{id}/` | Detail with recent media + posts |
| `POST /api/places/` | Create (title, description, city, category, latitude, longitude) |
| `GET /api/places/nearby/?lat=X&lng=Y&radius=10` | PostGIS proximity search (km) |
| `GET /api/places/{id}/stats/` | Rating avg/count, post count, media count |

### Media (auth required for upload/delete)

| Endpoint | Description |
|---|---|
| `GET /api/media/?place=ID` | List (returns presigned MinIO URLs) |
| `POST /api/media/` | Upload file (`multipart/form-data`: `file` + `place`) |
| `DELETE /api/media/{id}/` | Soft delete (owner only, also removes from MinIO) |

### Posts & Replies (auth required for write)

| Endpoint | Description |
|---|---|
| `GET /api/posts/?place=ID` | Top-level posts for a place |
| `GET /api/posts/{id}/` | Detail with replies, media, your vote |
| `POST /api/posts/` | Create (place, content, optional: parent, media) |
| `PATCH /api/posts/{id}/` | Edit content (owner only, marks `is_edited`) |
| `DELETE /api/posts/{id}/` | Soft delete (owner only) |
| `POST /api/posts/{id}/vote/` | Like/dislike (`{"is_like": true}`) — upsert |
| `DELETE /api/posts/{id}/vote/` | Remove vote |
| `GET /api/posts/{id}/replies/` | Paginated replies |

To create a **reply**, POST with `parent` set to the parent post ID.

### Ratings (auth required for write)

| Endpoint | Description |
|---|---|
| `GET /api/ratings/?place=ID` | Ratings for a place |
| `POST /api/ratings/` | Rate a place 1-5 (upsert per user/place) |
| `GET /api/ratings/my/` | Current user's ratings |

### Notifications (auth required)

| Endpoint | Description |
|---|---|
| `GET /api/notifications/` | Your notifications |
| `GET /api/notifications/unread-count/` | Unread count |
| `POST /api/notifications/{id}/read/` | Mark one as read |
| `POST /api/notifications/read-all/` | Mark all as read |

Notifications are auto-created when someone replies to, votes on, or reports your post.

### Reports (auth required)

| Endpoint | Description |
|---|---|
| `POST /api/reports/` | Report a post or media (`target_type`: `POST`/`MEDIA`, `reported_post`/`reported_media`, `reason`) |
| `GET /api/reports/` | Your reports |

## Project Structure

```
backend/
├── config/          # Django settings, root URLs, WSGI
├── tourism/         # Main app
│   ├── models.py        # ORM models (User, Place, Post, Media, Rating, etc.)
│   ├── serializers.py   # DRF serializers with MinIO upload + presigned URLs
│   ├── viewsets.py      # Business logic (CRUD, ownership, activity logging)
│   ├── auth_views.py    # Register/login/logout (bcrypt + JWT)
│   ├── permissions.py   # JWT token validation (cookie + Bearer)
│   ├── storage.py       # MinIO/S3 client (lazy init, auto bucket creation)
│   ├── utils.py         # Activity logging, notifications, file validation
│   ├── urls.py          # URL routing
│   └── views.py         # Health/ping endpoints
├── db/migrations/   # Raw SQL schema + seed data
└── reset_db.sh      # Drop & recreate schema
```

## Database

Schema managed via raw SQL (`db/migrations/`), not Django migrations. Run `bash reset_db.sh` to reset.

Tables: `users`, `provinces`, `cities`, `categories`, `places`, `media`, `posts`, `ratings`, `post_votes`, `activity_logs`, `notifications`, `reports`.

Key design decisions:
- PostGIS `GEOGRAPHY(POINT, 4326)` for place locations
- Soft deletes on `media` and `posts` (`deleted_at` column)
- Content moderation status enum (`PENDING_AI → PENDING_ADMIN → APPROVED/REJECTED`)
- One rating per user per place (unique constraint)
- One vote per user per post (unique constraint)
- Polymorphic reports (target_type + check constraint)
