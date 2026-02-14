import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = os.getenv("DEBUG", "0") == "1"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.auth",  # used for sessions + csrf (not user identity)
    "crm",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "crm.middleware.RequestIdentityMiddleware",
]

ROOT_URLCONF = "crm_service.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "crm" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "crm.context_processors.identity_context",
            ],
        },
    },
]

WSGI_APPLICATION = "crm_service.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "crm"),
        "USER": os.getenv("DB_USER", "crm"),
        "PASSWORD": os.getenv("DB_PASSWORD", "crm"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": int(os.getenv("DB_PORT", "3306")),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "var" / "static"

MEDIA_ROOT = os.getenv("MEDIA_ROOT", str(BASE_DIR / "var" / "media"))
MEDIA_URL = os.getenv("MEDIA_URL", "/media/")

REPORT_THRESHOLD = int(os.getenv("REPORT_THRESHOLD", "3"))

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
