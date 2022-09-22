#!/bin/bash

if [ -s "$SQLITE_DATABASE_PATH" ]; then
    # True if $SQLITE_DATABASE_PATH exists and has a size greater than zero.
    ls -la $SQLITE_DATABASE_PATH
else
    FIRST_RUN="True"
fi

python /app/manage.py migrate --noinput

if [ -n "$FIRST_RUN" ]; then
    echo "Creating initial user 'admin' with password 'password'."
    python /app/manage.py createsuperuser --noinput --username "admin" --password "password"
    unset $FIRST_RUN
fi

gunicorn --bind 0.0.0.0:8000 --pythonpath app config.wsgi --log-file -