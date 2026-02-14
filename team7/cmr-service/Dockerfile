FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends     default-libmysqlclient-dev gcc pkg-config     && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
ENV PYTHONUNBUFFERED=1

CMD ["bash", "-lc", "python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
