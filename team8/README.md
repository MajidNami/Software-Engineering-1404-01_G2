# Team 8: Comments, Media & Ratings System

Microservice for handling user-generated content in a tourism platform: comments, media uploads (photos/videos), and place ratings.

## Architecture

```
team8/
├── backend/          # Django REST API
├── frontend/         # React + Vite UI
├── ai-service/       # FastAPI ML service
├── db/               # PostgreSQL migrations
└── docker-compose.yml
```

## Services

- **Backend**: Django + DRF + PostgreSQL for REST API and data persistence
- **AI Service**: FastAPI for image tagging and spam detection
- **Frontend**: React for user interface
- **Gateway**: Nginx for routing and single entry point (port 9136)

## Quick Start

```bash
cd linux_scripts
./up-team.sh 8
```

Access points:
- Frontend: `http://localhost:9136`
- API: `http://localhost:9136/api/`
- Health: `http://localhost:9136/health`

## Database

PostgreSQL with automatic migration on startup. Manual migration:

```bash
docker exec -it team8-backend-1 python manage.py migrate
```

## API Endpoints

All endpoints require Core authentication cookie.

### Places
- `GET /api/places/` - List places
- `POST /api/places/` - Create place
- `GET /api/places/{id}/` - Place details
- `GET /api/places/{id}/comments/` - Place comments
- `GET /api/places/{id}/media/` - Place media

### Media
- `GET /api/media/` - List media
- `POST /api/media/` - Upload media
- `GET /api/media/{id}/` - Media details
- `PATCH /api/media/{id}/` - Update caption
- `DELETE /api/media/{id}/` - Soft delete

### Comments
- `GET /api/comments/` - List comments
- `POST /api/comments/` - Create comment
- `GET /api/comments/{id}/` - Comment details
- `PATCH /api/comments/{id}/` - Edit comment
- `DELETE /api/comments/{id}/` - Soft delete

### Ratings
- `GET /api/ratings/` - List ratings
- `POST /api/ratings/` - Rate place (1-5)
- `DELETE /api/ratings/{id}/` - Delete rating

### Reports
- `POST /api/reports/` - Report inappropriate content

### Notifications
- `GET /api/notifications/` - User notifications
- `PATCH /api/notifications/{id}/` - Mark as read

## Development

### Backend
```bash
cd team8/backend
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd team8/frontend
npm install
npm run dev
```

### AI Service
```bash
cd team8/ai-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

## Environment Variables

See `.env.example`:
- `TEAM8_DATABASE_URL` - PostgreSQL connection
- `CORE_BASE_URL` - Authentication service URL
- `AI_SERVICE_URL` - ML service URL
- `S3_ENDPOINT_URL` - Object storage URL

## Integration

- **Authentication**: Managed by Core service via cookies
- **User References**: Stored as UUID, not foreign keys
- **Database**: Independent PostgreSQL instance
- **Network**: All services communicate via `app404_net` Docker network

## Troubleshooting

Database reset:
```bash
docker-compose down -v
docker-compose up -d
```

Port conflicts: Check `TEAM_PORT=9136` in `.env`