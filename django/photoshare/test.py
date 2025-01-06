from photoshare.envs import TEST
from photoshare.settings import *

DEBUG = True
ENV = TEST

TEST_PATH = "tests/"
TEST_MEDIA_ROOT = os.path.join(BASE_DIR, "test_media/")
TEST_IMAGE_DIR = os.path.join(TEST_PATH, "images/")
TEST_DEBUG_TOOLBAR_SETTINGS = {
    "INTERCEPT_REDIRECTS": False,
    "SHOW_TOOLBAR_CALLBACK": lambda enable_toolbar: False,
}

ACCOUNT_EMAIL_VERIFICATION = "none"
EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"

MEDIA_ROOT = TEST_MEDIA_ROOT
DEBUG_TOOLBAR_CONFIG = TEST_DEBUG_TOOLBAR_SETTINGS

# https://docs.djangoproject.com/en/4.2/topics/testing/overview/
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
# Disable django restframework throttle rate for tests
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}
REST_FRAMEWORK["TEST_REQUEST_DEFAULT_FORMAT"] = "json"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "test_photoshare",
        "HOST": "localhost",
        "PORT": "5432",
        "USER": "postgres",
    }
}


print("\t\t###########################################")
print("\t\t###  Settings: test.py\t\t\t\t\t###")
print(f"\t\t###  Database: {DATABASES['default']['NAME']}\t\t\t###")
print("\t\t###########################################")
