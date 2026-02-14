FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    bash \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    curl \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
COPY team12/requirements.txt /app/team12_requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt && \
    pip install -r /app/team12_requirements.txt

COPY . /app/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]