from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    JWT_ACCESS_TTL_SECONDS=(int, 15 * 60),
    JWT_REFRESH_TTL_SECONDS=(int, 7 * 24 * 60 * 60),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-only-change-me")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

TEAM_APPS = [s.strip() for s in env("TEAM_APPS", default="team1,team2,team3,team4,team5,team6,team7,team8,team9").split(",") if s.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # 3rd-party
    "corsheaders",
    "rest_framework",
    "drf_spectacular",

    # Local
    "core",
    *TEAM_APPS,
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "core.middleware.JWTAuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app404.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "app404.wsgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

for t in TEAM_APPS:
    key = f"{t.upper()}_DATABASE_URL"

    default_url = f"sqlite:///{BASE_DIR / t / (t + '.sqlite3')}"
    DATABASES[t] = env.db(key, default=default_url)

DATABASE_ROUTERS = ["core.db_router.TeamPerAppRouter"]


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "http")

AUTH_USER_MODEL = "core.User"

JWT_SECRET = env("JWT_SECRET", default=SECRET_KEY)
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TTL_SECONDS = env("JWT_ACCESS_TTL_SECONDS")
JWT_REFRESH_TTL_SECONDS = env("JWT_REFRESH_TTL_SECONDS")

JWT_COOKIE_SECURE = env.bool("JWT_COOKIE_SECURE", default=False)
JWT_COOKIE_SAMESITE = env("JWT_COOKIE_SAMESITE", default="Lax")

CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^http://localhost:\d+$",
        r"^http://127\.0\.0\.1:\d+$",
    ]
else:
    CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])


CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# drf-spectacular Settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'Iran Explorer API',
    'DESCRIPTION': 'Comprehensive tourism and geography service system for Iran',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': r'/api/',
    'CONTACT': {
        'name': 'Software Engineering Team',
        'email': 'support@iranexplorer.ir',
    },
    'LICENSE': {
        'name': 'MIT License',
    },
    'SERVERS': [
        {
            'url': 'http://localhost:8000',
            'description': 'Development server',
        },
    ],
    'TAGS': [
        {'name': 'Authentication', 'description': 'User authentication and authorization'},
        {'name': 'Geography', 'description': 'Provinces, cities and geographic data'},
        {'name': 'Facilities', 'description': 'Hotels, restaurants, hospitals and other facilities'},
        {'name': 'Categories', 'description': 'Facility categories management'},
        {'name': 'Reviews', 'description': 'User reviews and ratings'},
        {'name': 'Favorites', 'description': 'User favorites management'},
        {'name': 'Regions', 'description': 'Region search and location services'},
        {'name': 'Wiki', 'description': 'Encyclopedia and knowledge base'},
        {'name': 'Media', 'description': 'Photos and reviews'},
        {'name': 'Recommendations', 'description': 'Smart destination recommendations'},
        {'name': 'Travel Planning', 'description': 'Trip planning and itinerary'},
        {'name': 'Maps', 'description': 'Interactive maps and geographic services'},
    ],
}