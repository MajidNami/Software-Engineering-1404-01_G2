#!/bin/bash
python manage.py collectstatic --noinput
echo "Starting server..."
exec gunicorn backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS}" \
    --timeout "${GUNICORN_TIMEOUT}"
