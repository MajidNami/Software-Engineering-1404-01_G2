# team8/backend/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# GeoDjango deps (you enabled django.contrib.gis)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    curl \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r /app/requirements.txt \
 && pip install gunicorn

COPY . /app

EXPOSE 8002

# DB is ready because compose uses depends_on healthcheck
CMD sh -c "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn wsgi:application --bind 0.0.0.0:8002 --workers 2 --timeout 120"

