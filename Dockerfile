FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential pkg-config default-libmysqlclient-dev \
    gcc libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
COPY --parents team*/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["bash","-lc","python manage.py migrate && python manage.py collectstatic --noinput && gunicorn app404.wsgi:application -b 0.0.0.0:8000 --workers 4"]
