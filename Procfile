release: python bookmarks/manage.py migrate --noinput
web: gunicorn --pythonpath bookmarks config.wsgi --log-file -