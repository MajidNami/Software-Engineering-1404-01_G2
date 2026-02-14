# راهنمای استقرار با Docker — تیم ۱۳

این سند نحوهٔ اجرای سرویس امکانات و حمل‌ونقل (team13) را با Docker و Docker Compose شرح می‌دهد.

---

## معماری

سرویس از دو کانتینر تشکیل شده است:

| سرویس | نقش | پورت (خارجی) |
|--------|-----|----------------|
| **gateway** | nginx؛ دریافت درخواست HTTP و پروکسی به بک‌اند | 8080 (قابل تغییر با `TEAM_PORT`) |
| **backend** | Django + Gunicorn؛ اپلیکیشن و مسیرهای `/team13/` | 8000 (فقط داخلی شبکه) |

جریان درخواست: مرورگر → gateway:80 → backend:8000

شبکهٔ استفاده‌شده: `app404_net` (external). حجم دادهٔ دیتابیس و آپلودها در volume با نام `team13_data` ذخیره می‌شود.

---

## پیش‌نیاز

- نصب **Docker** و **Docker Compose** (مثلاً Docker Desktop روی ویندوز/مک).
- ایجاد شبکهٔ مشترک (یک بار):

```bash
docker network create app404_net
```

در صورت وجود شبکه، این دستور خطا برمی‌گرداند؛ می‌توان نادیده گرفت.

---

## اجرا

همهٔ دستورات از **ریشهٔ پروژه** (پوشهٔ حاوی `manage.py` و پوشهٔ `team13`) اجرا شوند.

### بالا آوردن سرویس

```bash
docker compose -f team13/docker-compose.yml up -d --build
```

- `--build`: ساخت مجدد image بک‌اند در صورت تغییر Dockerfile یا کد.
- `-d`: اجرا در پس‌زمینه (detached).

### توقف

```bash
docker compose -f team13/docker-compose.yml down
```

حذف volume (دادهٔ دیتابیس و آپلودها):

```bash
docker compose -f team13/docker-compose.yml down -v
```

### مشاهدهٔ لاگ

```bash
docker compose -f team13/docker-compose.yml logs -f
```

---

## دسترسی به برنامه

پس از اجرا، از طریق gateway:

- آدرس پایه: `http://localhost:8080`
- صفحهٔ اصلی تیم ۱۳: `http://localhost:8080/team13/`

تغییر پورت: متغیر محیطی `TEAM_PORT` (مثلاً در `.env` در ریشهٔ پروژه یا قبل از دستور):

```bash
TEAM_PORT=9000 docker compose -f team13/docker-compose.yml up -d
```

---

## متغیرهای محیط

متغیرهای مهم برای سرویس **backend** در `docker-compose.yml` تعریف شده‌اند:

| متغیر | توضیح |
|--------|--------|
| `TEAM_APPS` | مقدار `team13` برای فعال بودن فقط این اپ |
| `TEAM13_DATABASE_URL` | مسیر SQLite داخل کانتینر؛ داده روی volume نگهداری می‌شود |
| `NESHAN_API_KEY_SERVICE` | کلید سرویس نشان (مسیریابی، جستجو، Geocoding) |
| `NESHAN_API_KEY_WEB` | کلید وب نشان (نقشه در فرانت) |

مقادیر پیش‌فرض کلیدهای نشان در `docker-compose.yml` و در **env.docker.example** آمده است. برای محیط واقعی می‌توان در `.env` مقداردهی کرد و با `docker compose` آن‌ها به کانتینر پاس داده می‌شوند.

---

## فایل‌های مرتبط

| فایل | کاربرد |
|------|--------|
| `team13/Dockerfile` | تعریف image بک‌اند: پایه پایتون ۳.۱۱، نصب وابستگی‌ها، کپی پروژه، اجرای migrate و Gunicorn |
| `team13/docker-compose.yml` | تعریف سرویس‌های backend و gateway، شبکه و volume |
| `team13/gateway.conf` | پیکربندی nginx (proxy به backend:8000) |
| `team13/env.docker.example` | نمونهٔ متغیرهای محیط برای پورت و کلید نشان |

ساخت image بک‌اند با **context** ریشهٔ پروژه و **dockerfile** برابر `team13/Dockerfile` انجام می‌شود تا کل پروژه (manage.py، app404، core، team13) در image قرار گیرد.

---

## Volume و ماندگاری داده

Volume با نام `team13_data` به مسیر `/app/data` داخل کانتینر backend متصل است. دیتابیس SQLite با `TEAM13_DATABASE_URL=sqlite:///app/data/team13.sqlite3` در این مسیر ایجاد می‌شود. با `down` بدون `-v` داده حفظ می‌شود؛ با `down -v` volume و داده حذف می‌شوند.

---

## عیب‌یابی

- **خطای شبکه وجود ندارد:** اجرای `docker network create app404_net`
- **پورت 8080 در استفاده:** تنظیم `TEAM_PORT` به پورت دیگر در `.env` یا در خط فرمان
- **خطا در مایگریشن یا دیتابیس:** بررسی لاگ با `docker compose -f team13/docker-compose.yml logs backend`؛ در صورت نیاز حذف volume با `down -v` و اجرای مجدد `up -d --build`
- **قطع یا timeout در pull تصاویر:** مشکل اتصال به Docker Hub؛ استفاده از آینهٔ registry یا VPN طبق راهنمای Docker در سیستم‌عامل
