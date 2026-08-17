#!/bin/bash

if [ -s "$SQLITE_DATABASE_PATH" ]; then
    # True if $SQLITE_DATABASE_PATH exists and has a size greater than zero.
    echo "Using database at $SQLITE_DATABASE_PATH"
else
    FIRST_RUN="True"
fi

if [ -z "$SKIP_STARTUP_MIGRATIONS" ]; then
    python /app/manage.py migrate --noinput
else
    echo "Not runing startup migrations"
fi 

if [ -n "$FIRST_RUN" ]; then
    echo "Creating initial user 'admin' with password 'password'."
    export DJANGO_SUPERUSER_PASSWORD=password
    python /app/manage.py createsuperuser --no-input --username "admin" --email "admin@example.com"
    unset $FIRST_RUN
fi

# opentelemetry-instrumentation-django reads DJANGO_SETTINGS_MODULE and imports
# the settings module during OTel's sitecustomize bootstrap — which runs before
# gunicorn parses --pythonpath. Both env vars are needed: without
# DJANGO_SETTINGS_MODULE the instrumentor calls settings.configure(); without
# /app on PYTHONPATH the settings module fails to import and it ALSO calls
# settings.configure(). Either path leaves _wrapped pinned to a
# UserSettingsHolder, so wsgi.py's setdefault becomes a no-op and every
# settings access falls through to django.conf.global_settings.
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.production}"
export PYTHONPATH="/app${PYTHONPATH:+:$PYTHONPATH}"

exec opentelemetry-instrument gunicorn --bind 0.0.0.0:8000 config.wsgi --log-file -