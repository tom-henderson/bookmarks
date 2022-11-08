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

gunicorn --bind 0.0.0.0:8000 --pythonpath app config.wsgi --log-file -