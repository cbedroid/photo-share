import os
from pathlib import Path

from dotenv import load_dotenv

from .config.allauth_config import *  # noqa: F401
from .debug_toolbar_config import *  # noqa: F401

load_dotenv()
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = int(os.getenv("DEBUG", default=0))

if DEBUG:
    ACCOUNT_EMAIL_VERIFICATION = "none"


ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(" ")
# Application definition

ALLAUTH_APPS = [
    # The following apps are required:
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_social_share",
    "debug_toolbar",
    "rest_framework",
    "profanity",
    "widget_tweaks",
    "crispy_forms",
    "users",
    "core",
    "gallery",
    "django_cleanup",
] + ALLAUTH_APPS


# SITE ID
SITE_ID = 1

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "photoshare.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "photoshare.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.getenv("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.getenv("SQL_USER", "user"),
        "PASSWORD": os.getenv("SQL_PASSWORD", "password"),
        "HOST": os.getenv("SQL_HOST", "localhost"),
        "PORT": os.getenv("SQL_PORT", "5432"),
    }
}


# REDIS
REDIS_TTL_TIMEOUT = None
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,  # seconds
            "SOCKET_TIMEOUT": 5,  # seconds
            # https://redis.io/topics/security
            # For future production server, this will need to be configured manually.
            # Highly recommended to protect sensitive data  - minimum: 60+ chars.
            "PASSWORD": os.getenv("REDIS_PASSWORD"),
        },
    }
}

# Configure Redis to handle Django session cache
# https://github.com/jazzband/django-redis#configure-as-session-backend
# NOTE: May have to change this during testing... Maybe..reading more docs on this
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "core:index"
LOGOUT_REDIRECT_URL = "core:index"
ACCOUNT_ADAPTER = "users.adapters.AccountAdapter"


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = "bootstrap4"


STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"


JAZZMIN_SETTINGS = {
    # title of the window
    "site_title": "Photo-Share Admin",
    # Title on the brand, and the login screen (19 chars max)
    "site_header": "PHOTO-SHARE",
    # square logo to use for your site, must be present in static files, used for favicon and brand on top left
    "site_logo": "static/assets/images/PhotoShare-logo.png",
    # Welcome text on the login screen
    "welcome_sign": "Welcome to Photo-Share",
    # Copyright on the footer
    "copyright": "NowOrNever LLC",
    # The model admin to search from the search bar, search bar omitted if excluded
    "search_model": "users.User",
    # Order the auth app before the books app, other apps will be alphabetically placed after these
    "order_with_respect_to": [
        "users",
        "account",
        "gallery",
        "auth",
    ],
    # Custom icons for side menu apps/models
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "account.emailaddress": "fas fa-envelope",
        "account_profile.account": "fa fa-user-cog",
        "gallery.category": "fa fa-th-list",
        "gallery.gallery": "fa fa-images",
        "gallery.photo": "fa fa-image",
        "gallery.rate": "fa fa-thumbs-up",
        "gallery.tag": "fa fa-tags",
        "sites.sites": "fas fa-globe",
        "socialaccount.socialapp": "fab fa-app-store-ios",
        "users.user": "fas fa-users",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to show the UI customized on the sidebar
    "show_ui_builder": False,
}


# To run behind HTTPS proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"],
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "120/min",
    },
    "NUM_PROXIES": 1,
}

# ********************* #
# *** Email Service *** #
# # ********************* #
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = os.getenv("SUPPORT_EMAIL_HOST", "DebuggingServer")
# EMAIL_PORT = os.getenv("SUPPORT_EMAIL_PORT", 587)
