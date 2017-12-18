# Bookmarks

Bookmark manager to replace del.icio.us.

## Libraries Used:

### Django
- [Django](https://www.djangoproject.com/)
- [Django REST Framework](http://www.django-rest-framework.org/)
- [dj-database-url](https://github.com/kennethreitz/dj-database-url)
- [whitenoise](https://github.com/evansd/whitenoise)
- [django-taggit](https://github.com/alex/django-taggit)
- [django-taggit-helpers](https://github.com/mfcovington/django-taggit-helpers)
- [django-taggit-serializer](https://github.com/glemmaPaul/django-taggit-serializer)

### JavaScript
- [bloodhound](https://github.com/twitter/typeahead.js)
- [typeahead](https://github.com/twitter/typeahead.js)
- [bootstrap-datepicker](https://github.com/eternicode/bootstrap-datepicker)
- [bootstrap-tagsinput](https://github.com/bootstrap-tagsinput/bootstrap-tagsinput)
- [chart.js](https://github.com/chartjs/Chart.js)

### Integrations
- Heroku Slack Webhooks

## Bookmarklet
```
javascript:(function($){url='http://127.0.0.1:8000/new/';url+='?url='+encodeURIComponent(window.location.href);url+='&title='+encodeURIComponent(document.title);url+='&description='+encodeURIComponent(''+(window.getSelection?window.getSelection():document.getSelection?document.getSelection():document.selection.createRange().text));window.open(url,"_self");})();
```

### Django 2.0

Create python3 virtual environment

```
python3 -m venv .env
source .env/bin/activate
pip install -r requirements/local.txt
python bookmarks/manage.py runserver
```
