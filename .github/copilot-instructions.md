# Bookmarks - AI Coding Agent Instructions

## Project Overview
Django-based bookmark manager (del.icio.us replacement) with REST API, tagging, and Slack integration. Uses Django REST Framework with Bootstrap/jQuery frontend and multi-stage Docker builds.

## Architecture

### Directory Structure Pattern
- **Nested Django Structure**: Project lives in `bookmarks/` subdirectory (not workspace root)
- **Settings Split**: `config/settings/{base,local,production,test}.py` - environment-specific configs inherit from base
- **Config Module**: `bookmarks/config/` contains settings, urls, wsgi (not traditional `project_name/` at root)
- **Dual Templates**: App templates in `bookmarks/templates/bookmarks/`, project-wide in `config/templates/`

### Key Components
- **Model**: Single `Bookmark` model ([bookmarks/models.py](../bookmarks/bookmarks/models.py)) with django-taggit integration
- **API**: Django REST Framework views in [api/api.py](../bookmarks/api/api.py) - returns public bookmarks only
- **Frontend**: Server-rendered Django templates + Bootstrap 3 + jQuery typeahead/tokenfield
- **Static Assets**: npm packages via django-npm, served through whitenoise with compression

## Development Workflows

### Local Setup
```bash
# From workspace root
npm install  # Frontend dependencies
python3 -m venv .env && source .env/bin/activate
pip install -r requirements.txt
python bookmarks/manage.py migrate
python bookmarks/manage.py collectstatic
python bookmarks/manage.py runserver
```

**Critical**: All Django commands run from workspace root with path `bookmarks/manage.py`, NOT from inside bookmarks/

### Docker Development
Multi-stage build ([Dockerfile](../Dockerfile)):
1. `base`: Python deps + git for private package (django-common)
2. `node`: npm install for Bootstrap/jQuery
3. `staticfiles`: Runs collectstatic combining npm + Django statics
4. Final: Runtime with gunicorn, auto-creates admin user on first run

```bash
docker build -t bookmarks .
docker run -p 8000:8000 -v ./data:/data bookmarks
# Default admin:password on first run
```

### Testing
```bash
# Use test settings (in-memory SQLite)
DJANGO_SETTINGS_MODULE=config.settings.test python bookmarks/manage.py test
```

## Project Conventions

### Settings Pattern
- Import via `from .base import *` in environment files
- Use `get_env_setting()` helper for env vars with defaults (see [base.py](../bookmarks/config/settings/base.py#L9-L17))
- `NPM_FILE_PATTERNS` dict defines which npm package files to collect (whitelist approach)

### Model & View Patterns
- **Taggit Integration**: Use `TaggableManager()` for tags, query with `prefetch_related('tags')`
- **Privacy**: `private` boolean field - filter `private=False` for unauthenticated users
- **Class-Based Views**: Inherit from `LoginRequiredMixin` (django-common) for auth
- **Form Mixins**: Use `BootStrapForm` and `NextOnSuccessMixin` from django-common package

### API Conventions
- Public endpoints only return `private=False` bookmarks
- CORS header manually added in `API_RecentBookmarks.get()` for cross-origin access
- Taggit serialization via `TaggitSerializer` mixin + `TagListSerializerField`

### Signal-Based Integrations
Post-save signal on Bookmark ([models.py](../bookmarks/bookmarks/models.py#L27-L49)) sends Slack webhook if `SLACK_WEBHOOK_URL` setting exists. Gracefully skips if setting absent.

### Management Commands
Custom commands in `bookmarks/management/commands/` - example: `importbookmarks.py` imports JSON with datetime logging pattern

## Dependencies
- **Private Repo**: Requires `django-common` from GitHub (git+https://...) - contains shared mixins
- **Pinned Versions**: Django 5.1.3, DRF 3.15.2, Bootstrap 3.4.1 - avoid upgrading without testing frontend compatibility
- **Frontend Stack**: jQuery 3.5.1 + typeahead.js for tag autocomplete, bootstrap-tokenfield for tag input

## Deployment Notes
- GitHub Actions builds on master push → tags with `BASE_VERSION.RUN_NUMBER` → pushes to GitHub Packages
- Entrypoint ([entrypoint.sh](../entrypoint.sh)) auto-migrates and creates superuser on fresh DB
- Uses whitenoise compressed static files (no separate web server needed for statics)
- SQLite database path from `SQLITE_DATABASE_PATH` env var, defaults to `bookmarks/db.sqlite3`

## Anti-Patterns to Avoid
- ❌ Don't run manage.py from inside bookmarks/ directory
- ❌ Don't bypass privacy filters in API endpoints
- ❌ Don't assume standard Django project structure (config != project_name)
- ❌ Don't import settings directly - use environment-specific entry points
