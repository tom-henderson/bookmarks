"""Development settings and globals."""
from .base import *


# DEBUG CONFIGURATION
DEBUG = True
INTERNAL_IPS = ('127.0.0.1',)
ALLOWED_HOSTS = ['*']

# EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CACHE CONFIGURATION
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# FIXTURE CONFIGURATION
FIXTURE_DIRS = (
    os.path.join(PROJECT_ROOT, 'fixtures'),
)
