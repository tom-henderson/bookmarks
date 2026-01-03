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