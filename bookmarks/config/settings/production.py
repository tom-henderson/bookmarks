"""Production settings and globals."""
from .base import *


# SECRET CONFIGURATION
SECRET_KEY = get_env_setting('SECRET_KEY')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HOST CONFIGURATION
ALLOWED_HOSTS = ['*']

# EMAIL CONFIGURATION
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = environ.get('EMAIL_HOST', 'smtp.gmail.com')
# EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')
# EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'your_email@example.com')
# EMAIL_PORT = environ.get('EMAIL_PORT', 587)
# EMAIL_SUBJECT_PREFIX = '[{}] '.format(SITE_NAME)
# EMAIL_USE_TLS = True
# SERVER_EMAIL = EMAIL_HOST_USER

# DJANGO REST FRAMEWORK
# Disable the browsable HTTP API
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

# SLACK INTEGRATION
SLACK_WEBHOOK_URL = get_env_setting('SLACK_WEBHOOK_URL')
