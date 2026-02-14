#!/usr/bin/env bash
set -euo pipefail

cd /app

if [[ ! -f manage.py ]]; then
  echo "ERROR: manage.py not found in /app."
  echo "Build with repo-root context and dockerfile=team8/Dockerfile (so manage.py/app404 are included)."
  exit 1
fi

: "${DJANGO_SETTINGS_MODULE:=app404.settings}"
: "${WSGI_MODULE:=app404.wsgi:application}"
: "${PORT:=8000}"
export DJANGO_SETTINGS_MODULE

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn "$WSGI_MODULE" \
  --bind "0.0.0.0:${PORT}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-120}"

