import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, True))
# First try backend/.env, then fall back to team8/.env
env_file = BASE_DIR / ".env"
if not env_file.exists():
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
    "tourism",  # Our app
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    # Team8 tables - Your PostgreSQL with PostGIS
    "default": env.db(
        "TEAM8_DATABASE_URL",
        default="postgresql://team8_user:team8_pass@postgres:5432/team8_db",
        engine="django.contrib.gis.db.backends.postgis"
    )
}

# No custom AUTH_USER_MODEL - we store user_id as UUID, not ForeignKey
# AUTH_USER_MODEL = None  # Removed - causes issues with makemigrations

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
    "DEFAULT_PERMISSION_CLASSES": ["tourism.permissions.IsAuthenticated"],
    "EXCEPTION_HANDLER": "tourism.utils.custom_exception_handler",
}

CORS_ALLOW_CREDENTIALS = True
if DEBUG:
    CORS_ALLOWED_ORIGIN_REGEXES = [r"^http://localhost:\d+$", r"^http://127\.0\.0\.1:\d+$"]
else:
    CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# JWT
JWT_SECRET = SECRET_KEY
JWT_ALGORITHM = "HS256"
JWT_EXP_DAYS = 30

# S3 / MinIO
S3_ENDPOINT_URL = env("S3_ENDPOINT_URL", default="http://localhost:9000")
S3_ACCESS_KEY = env("S3_ACCESS_KEY", default="minioadmin")
S3_SECRET_KEY = env("S3_SECRET_KEY", default="minioadmin123")
S3_BUCKET_NAME = env("S3_BUCKET_NAME", default="team8-media")

# Upload limits
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/webm", "video/quicktime"]

# AI Service
AI_SERVICE_URL = env("AI_SERVICE_URL", default="http://localhost:8002")
INTERNAL_API_KEY = env("INTERNAL_API_KEY", default="team8-internal-secret-change-me")

# AI Moderation thresholds
# Scores above REJECT → REJECTED, between REVIEW and REJECT → PENDING_ADMIN, below REVIEW → APPROVED
AI_REJECT_THRESHOLD = float(env("AI_REJECT_THRESHOLD", default="0.8"))
AI_REVIEW_THRESHOLD = float(env("AI_REVIEW_THRESHOLD", default="0.4"))
