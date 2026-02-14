# Dockerfile برای سرویس امکانات و حمل‌ونقل (تیم ۱۳)
# پروژهٔ Django از ریشهٔ مخزن (پوشهٔ بالاتر) اجرا می‌شود؛ این فایل باید با context ریشه ساخته شود.

FROM python:3.11-slim

# جلوگیری از نوشتن فایل‌های .pyc و بافر کردن خروجی
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# نصب وابستگی‌های سیستمی (در صورت نیاز برای mysqlclient و غیره)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# کپی و نصب وابستگی‌های پایتون (ریشه + team13)
COPY requirements.txt .
COPY team13/requirements.txt team13/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r team13/requirements.txt

# کپی کل پروژه (مدیریت، app404، core، team13 و ...)
COPY . .

# جمع‌آوری فایل‌های استاتیک (برای سرو با whitenoise)
RUN python manage.py collectstatic --noinput --settings=app404.settings 2>/dev/null || true

# پورت اپلیکیشن
EXPOSE 8000

# اجرای مایگریشن و سپس سرور با Gunicorn
# متغیرهای محیطی: TEAM_APPS، DATABASE_URL، TEAM13_DATABASE_URL و غیره از docker-compose یا env می‌آیند.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn app404.wsgi:application --bind 0.0.0.0:8000 --workers 2 --threads 2 --timeout 60"]
