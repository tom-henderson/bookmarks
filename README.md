# Bookmarks

Bookmark manager to replace del.icio.us.

[![Updates](https://pyup.io/repos/github/tom-henderson/bookmarks/shield.svg)](https://pyup.io/repos/github/tom-henderson/bookmarks/)
[![Python 3](https://pyup.io/repos/github/tom-henderson/bookmarks/python-3-shield.svg)](https://pyup.io/repos/github/tom-henderson/bookmarks/)
[![Known Vulnerabilities](https://snyk.io/test/github/tom-henderson/bookmarks/badge.svg)](https://snyk.io/test/github/tom-henderson/bookmarks)


## Libraries Used:

### Django
- [Django](https://www.djangoproject.com/)
- [Django REST Framework](http://www.django-rest-framework.org/)
- [dj-database-url](https://github.com/kennethreitz/dj-database-url)
- [whitenoise](https://github.com/evansd/whitenoise)
- [django-taggit](https://github.com/alex/django-taggit)
- [django-taggit-helpers](https://github.com/mfcovington/django-taggit-helpers)
- [django-npm](https://github.com/kevin1024/django-npm)

### JavaScript
- [typeahead](https://github.com/twitter/typeahead.js)
- [bootstrap-datepicker](https://github.com/eternicode/bootstrap-datepicker)
- [bootstrap-tokenfield](https://github.com/sliptree/bootstrap-tokenfield)

### Integrations
- Heroku Slack Webhooks

## Trusted proxy header (remote user) authentication

Optional, and **disabled by default**. When the app runs behind a reverse proxy
that authenticates users itself (e.g. Traefik `forwardAuth` with Tinyauth /
Pocket ID), the proxy can pass the logged-in user's identity in a request
header and Django will log that user in automatically. The normal
username/password login keeps working as a fallback.

| Variable | Default | Description |
| --- | --- | --- |
| `REMOTE_USER_HEADER` | _(unset)_ | Header carrying the user identity as sent on the wire, e.g. `Remote-User`. Unset or empty disables the feature completely (the middleware and backend are not installed). |
| `REMOTE_USER_FIELD` | `username` | User field matched against the header value: `username` or `email` (email matching is case-insensitive; if several users share the email, login is refused and a warning is logged). |
| `REMOTE_USER_CREATE_UNKNOWN` | `false` | `true` to create a user when no match is found. With `username`, the email is taken from the `Remote-Email` header if present; with `email`, the email is used as both email and username. New users have an unusable password and no staff rights. |
| `REMOTE_USER_GROUPS_HEADER` | _(unset)_ | Header carrying comma-separated group names, e.g. `Remote-Groups`. |
| `REMOTE_USER_ADMIN_GROUPS` | _(unset)_ | Comma-separated group names, e.g. `admins`. When this **and** `REMOTE_USER_GROUPS_HEADER` are set, every proxy login sets `is_staff` and `is_superuser` to whether the user is in one of these groups (granted and revoked). If either is unset, those flags are never changed. |

Example (Docker environment):

```yaml
environment:
  REMOTE_USER_HEADER: Remote-User
  REMOTE_USER_FIELD: username
  REMOTE_USER_CREATE_UNKNOWN: "false"
  REMOTE_USER_GROUPS_HEADER: Remote-Groups
  REMOTE_USER_ADMIN_GROUPS: admins
```

The session is persistent: the header only needs to be present on the routes
that go through the proxy's auth (e.g. `/login/` and `/admin/`), and the user
stays logged in elsewhere. If the header later names a different user, a
session created from the header is replaced with that user.

> **Security warning:** the header is trusted blindly. Only enable this when
> the app is reachable **exclusively** through a proxy that sets these headers
> on authenticated routes and strips any client-supplied `Remote-*` headers on
> **every** route (including public ones). If the container port is reachable
> directly, or any route forwards client headers unchanged, anyone can log in
> as any user, including an admin.

## Testing

```bash
pip install -r requirements.txt && npm install
cd bookmarks && DJANGO_SETTINGS_MODULE=config.settings.test python manage.py test bookmarks api
```

See [TESTING.md](TESTING.md) for full details on what is tested and how CI works.

## Bookmarklet
```
javascript:(function($){url='http://127.0.0.1:8000/new/';url+='?url='+encodeURIComponent(window.location.href);url+='&title='+encodeURIComponent(document.title);url+='&description='+encodeURIComponent(''+(window.getSelection?window.getSelection():document.getSelection?document.getSelection():document.selection.createRange().text));window.open(url,"_self");})();
```

### Django 2.0

Create python3 virtual environment

```
npm install
python3 -m venv .env
source .env/bin/activate
pip install -r requirements/local.txt
python bookmarks/manage.py migrate
python bookmarks/manage.py collectstatic
python bookmarks/manage.py runserver
```