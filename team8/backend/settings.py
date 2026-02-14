import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

env = environ.Env(DEBUG=(bool, True))
env_file = BASE_DIR.parent / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

DEBUG = env("DEBUG")
SECRET_KEY = env("DJANGO_SECRET_KEY", default="team8-dev-secret-change-me")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "backend"])

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.gis",  # GeoDjango for PostGIS
    "rest_framework",
    "rest_framework_gis",  # DRF GIS support
    "corsheaders",
    "django_filters",
    "backend",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "urls"
WSGI_APPLICATION = "wsgi.application"

DATABASES = {
    # Team8 tables - Your PostgreSQL
    "default": env.db(
        "TEAM8_DATABASE_URL",
        default="postgresql://team8_user:team8_pass@postgres:5432/team8_db"
    )
}

# No AUTH_USER_MODEL - we store user_id as UUID, not ForeignKey
AUTH_USER_MODEL = None

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["permissions.IsAuthenticatedViaCookie"],
    "EXCEPTION_HANDLER": "utils.custom_exception_handler",
}

CORS_ALLOW_CREDENTIALS = True
if DEBUG:
    CORS_ALLOWED_ORIGIN_REGEXES = [r"^http://localhost:\d+$", r"^http://127\.0\.0\.1:\d+$"]
else:
    CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

CORE_BASE_URL = env("CORE_BASE_URL", default="http://core:8000")
AI_SERVICE_URL = env("AI_SERVICE_URL", default="http://ai-service:8001")

S3_BUCKET_NAME = env("S3_BUCKET_NAME", default="team8-media")
S3_ENDPOINT_URL = env("S3_ENDPOINT_URL", default="")
S3_ACCESS_KEY = env("S3_ACCESS_KEY", default="")
S3_SECRET_KEY = env("S3_SECRET_KEY", default="")

MAX_UPLOAD_SIZE = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/webm", "video/quicktime"]
