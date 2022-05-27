import os
from datetime import timedelta
from marshmallow.validate import OneOf
from environs import Env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ID = 1


def join(path):
    return os.path.join(BASE_DIR, path)


env = Env(expand_vars=True)
env.read_env(recurse=False, path=join(".env"), override=True)  # noqa

PROJECT_NAME = env("PROJECT_NAME")
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG")
ENV_LEVEL = env("ENV_LEVEL")
CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

WSGI_APPLICATION = "core_config.wsgi.application"
ASGI_APPLICATION = "core_config.asgi.application"

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_yasg",
    "corsheaders",
    "rest_framework",
    "django_celery_results",
    "django_filters",
    "solo",
    "account.apps.AccountConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core_config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Uncomment when frontend is SSR
                # "utils.utils.get_webpack_context",
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

with env.prefixed("DB_") as e:
    DATABASES = {
        "default": dict(
            ENGINE="django.db.backends.postgresql_psycopg2",
            NAME=e("NAME"),
            USER=e("USER"),
            PASSWORD=e("PASS"),
            HOST=e("HOST"),
            PORT=e("PORT"),
        )
    }

with env.prefixed("REDIS_") as e:
    REDIS = "redis://{}:{}".format(e("HOST").strip(), str(e.int("PORT")))
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [(e("HOST").strip(), e.int("PORT"))],
            },
        },
    }

AUTH_USER_MODEL = "account.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=env.int("ACCESS_TOKEN_LIFETIME", 1)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("REFRESH_TOKEN_LIFETIME", 5)),
    "AUTH_HEADER_TYPES": ("Bearer", "jwt"),
}
CACHE_TTL = 90
CACHES = {
    "default": dict(
        BACKEND="django_redis.cache.RedisCache",
        TIMEOUT=CACHE_TTL,
        LOCATION=REDIS,
        OPTIONS=dict(
            DB=0,
            PARSER_CLASS="redis.connection.HiredisParser",
            CONNECTION_POOL_CLASS="redis.BlockingConnectionPool",
            CONNECTION_POOL_CLASS_KWARGS=dict(max_connections=50, timeout=20),
            MAX_CONNECTIONS=1000,
            PICKLE_VERSION=-1,
        ),
    )
}
# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR + "/media/"
STATIC_ROOT = BASE_DIR + "/static_cdn/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

REST_FRAMEWORK = dict(
    DEFAULT_PERMISSION_CLASSES=("rest_framework.permissions.IsAuthenticated",),
    DEFAULT_AUTHENTICATION_CLASSES=(
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    UNAUTHENTICATED_USER=None,
    DEFAULT_RENDERER_CLASSES=("rest_framework.renderers.JSONRenderer",),
    DEFAULT_PAGINATION_CLASS="utils.views.CustomPagination",
    DEFAULT_FILTER_BACKENDS=("django_filters.rest_framework.DjangoFilterBackend",),
)

SWAGGER_SETTINGS = dict(
    DEFAULT_AUTO_SCHEMA_CLASS="utils.schema.CustomSwaggerAutoSchema",
    SECURITY_DEFINITIONS=dict(
        Token={"type": "apiKey", "name": "Authorization", "in": "header"}
    ),
    JSON_EDITOR=True,
    VALIDATOR_URL=None,
    SHOW_REQUEST_HEADERS=False,
    APIS_SORTER="alpha",
    DEEP_LINKING=True,
    USE_SESSION_AUTH=True,
    REFETCH_SCHEMA_WITH_AUTH=True,
    PERSIST_AUTH=False,
    DOC_EXPANSION="none",
    DEFAULT_PAGINATOR_INSPECTORS=(
        "utils.schema.CustomPaginationSchema",
        "drf_yasg.inspectors.CoreAPICompatInspector",
    ),
    DEFAULT_FIELD_INSPECTORS=(
        "utils.drf_inspectors.RangeFieldInspector",
        "utils.drf_inspectors.ChoiceFieldInspector",
        "drf_yasg.inspectors.CamelCaseJSONFilter",
        "drf_yasg.inspectors.RecursiveFieldInspector",
        "drf_yasg.inspectors.ReferencingSerializerInspector",
        "drf_yasg.inspectors.FileFieldInspector",
        "drf_yasg.inspectors.DictFieldInspector",
        "drf_yasg.inspectors.HiddenFieldInspector",
        "drf_yasg.inspectors.RelatedFieldInspector",
        "drf_yasg.inspectors.SerializerMethodFieldInspector",
        "drf_yasg.inspectors.SimpleFieldInspector",
        "drf_yasg.inspectors.StringDefaultFieldInspector",
    ),
)


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail.hackerbiz.com"
EMAIL_HOST_USER = env("EMAIL_HOST_USER", 1)
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", 1)
EMAIL_PORT = 2525

# celery
CELERY_BROKER_URL = REDIS + "/1"
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# captcha setting
# https://developers.google.com/recaptcha/docs/verify
CAPTCHA_TYPE = env.str(
    "CAPTCHA_TYPE",
    validate=OneOf(
        ["recaptcha", "none"],
        error="CAPTCHA_TYPE must be one of: {choices}",
    ),
)
RECAPTCHA_SECRET = ""
if CAPTCHA_TYPE == "recaptcha":
    RECAPTCHA_SECRET = env("RECAPTCHA_SECRET")
RECAPTCHA_URL = "https://www.google.com/recaptcha/api/siteverify"
