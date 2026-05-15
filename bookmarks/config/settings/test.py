from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

# Plain storage so collectstatic and {% static %} work without a pre-built manifest
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
