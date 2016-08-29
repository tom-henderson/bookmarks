"""Production settings and globals."""
from .base import *
import dj_database_url

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return os.environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)


# SECRET CONFIGURATION
SECRET_KEY = get_env_setting('SECRET_KEY')

# HOST CONFIGURATION
ALLOWED_HOSTS = []

# EMAIL CONFIGURATION
# See:
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')
#EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')
#EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'your_email@example.com')
#EMAIL_PORT = environ.get('EMAIL_PORT', 587)
#EMAIL_SUBJECT_PREFIX = '[{}] '.format(SITE_NAME)
#EMAIL_USE_TLS = True
#SERVER_EMAIL = EMAIL_HOST_USER

# DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DJANGO_ROOT, 'db.sqlite3'),
    }
}
# Update database configuration with $DATABASE_URL.
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

# CACHE CONFIGURATION
CACHES = {}


# LOGGING CONFIGURATION
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}