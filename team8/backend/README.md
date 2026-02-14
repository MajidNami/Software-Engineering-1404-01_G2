# Backend Service

Django REST Framework API for comments, media uploads, and ratings.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## Database Migrations

After modifying `models.py`:

```bash
python manage.py makemigrations
python manage.py migrate
```

In Docker:
```bash
docker exec -it team8-backend-1 python manage.py migrate
```

## API Authentication

All endpoints require authentication via Core service cookies. The `IsAuthenticatedViaCookie` permission class:

1. Extracts `access_token` cookie from request
2. Validates with Core service at `CORE_BASE_URL/api/auth/verify/`
3. Populates `request.user_data` with user info:
   ```python
   {
       "id": "uuid",
       "email": "user@example.com",
       "first_name": "...",
       "last_name": "..."
   }
   ```

Usage in views:
```python
user_id = self.request.user_data["id"]
```

## Configuration

- `settings.py` - Django settings
- `urls.py` - URL routing
- `wsgi.py` - WSGI entry point
- `manage.py` - Management commands

## Code Structure

- `models.py` - Database models
- `serializers.py` - DRF serializers
- `viewsets.py` - DRF viewsets
- `permissions.py` - Custom permissions
- `utils.py` - Helper functions

## Testing

```bash
python manage.py test
```
