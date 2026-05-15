# Testing

## Running Tests Locally

```bash
# Install dependencies first
pip install -r requirements.txt
npm install

# Run all tests
cd bookmarks
DJANGO_SETTINGS_MODULE=config.settings.test python manage.py test bookmarks api --verbosity=2

# Run a specific test module
DJANGO_SETTINGS_MODULE=config.settings.test python manage.py test bookmarks.tests.test_models

# Verify static file collection (catches JS package breakage)
DJANGO_SETTINGS_MODULE=config.settings.test python manage.py collectstatic --noinput
```

The test suite uses an in-memory SQLite database and MD5 password hashing for speed. No external services are required.

## What is Tested

### `bookmarks/tests/test_models.py`

**`BookmarkModelTests`** — validates the `Bookmark` model's fields and constraints:
- Required fields (only `url` is required)
- Optional `title` and `description` fields (nullable)
- Default values: `private=False`, `date_added` set to now
- Field length limits (url: 500 chars, title: 200 chars)
- Tag addition and retrieval via `django-taggit`
- Case-insensitive tag deduplication (`TAGGIT_CASE_INSENSITIVE=True`)
- String representation

**`BookmarkSignalTests`** — validates the post-save Slack webhook signal:
- No HTTP call when `SLACK_WEBHOOK_URL` is not configured
- HTTP call made with correct payload when webhook is configured
- Signal fires only on create, not on update
- Network exceptions are silenced and don't crash the save

### `bookmarks/tests/test_views.py`

**`BookmarksListViewTests`** — the main list view (`/`):
- Anonymous users see only public bookmarks; authenticated users see private ones too
- Search works across title, description, and tags
- Date range filtering (`date_added_from`, `date_added_to`)
- Pagination (20 bookmarks per page)
- Activity chart data is present in context
- Newest bookmarks appear first
- `search` context variable only set when a search term is present

**`BookmarkTagListViewTests`** — tag-filtered list (`/tag/<slug>/`):
- Filters to only bookmarks with the specified tag
- Context title includes the tag name
- Returns 404 for a tag slug that doesn't exist
- Respects public/private visibility

**`BookmarkCreateViewTests`** — create bookmark form (`/new/`):
- Redirects anonymous users to login
- Authenticated users get the form
- GET parameters (`url`, `title`, `description`) pre-fill form initial values
- Valid POST creates a bookmark and redirects
- Invalid/missing URL shows form errors

**`BookmarkUpdateViewTests`** — edit bookmark form (`/edit/<pk>/`):
- Redirects anonymous users to login
- Authenticated users get the form
- Valid POST updates the bookmark
- Returns 404 for a non-existent bookmark pk

**`ChartsViewTests`** — activity history page (`/charts/`):
- Renders correctly with no bookmarks (empty `activity_years`)
- Builds one chart entry per calendar year spanned by bookmarks
- Authenticated users include private bookmarks in charts; anonymous don't

**`AuthViewTests`** — login/logout:
- Login page renders
- Valid credentials redirect; invalid credentials re-render the form
- Logout redirects

**`StaticFileFinderTests`** — npm package integration:
- Verifies that each JavaScript package referenced in `NPM_FILE_PATTERNS` exposes its expected files via Django's static file finders
- Automatically **skipped** when `node_modules/` is absent (e.g. pure Python unit test runs)
- **Runs in CI** where `npm install` is always executed
- Catches path changes caused by JavaScript package major version upgrades

### `bookmarks/tests/test_utils.py`

**`BuildActivityChartTests`** — the `build_activity_chart()` utility function:
- Returns a dict with `weeks` and `month_labels`
- All counts are 0 for an empty queryset
- Level thresholds: 0→level 0, 1-2→level 1, 3-4→level 2, 5-7→level 3, 8+→level 4
- Bookmarks appear on the correct calendar date
- Day titles use correct singular/plural ("1 bookmark" vs "2 bookmarks")
- `clickable` is True only for days with bookmarks
- Month labels are valid abbreviations
- At least 12 month labels are generated for a full year
- Queryset filters are respected (e.g. excluding private bookmarks)

### `bookmarks/tests/test_management.py`

**`ImportBookmarksCommandTests`** — the `importbookmarks` management command:
- Creates the correct number of bookmarks from a JSON file
- All fields are set correctly (url, title, description, private)
- Tags are added
- An empty JSON array creates no bookmarks
- A non-existent file path raises an exception

### `api/tests/test_api.py`

**`APIBookmarksTests`** — `GET /api/all/`:
- Returns 200 with JSON content type
- Includes public bookmarks, excludes private ones
- Response includes all expected fields (title, description, date_added, tags, private, url)
- Tags are serialised as a list of strings

**`APIRecentBookmarksTests`** — `GET /api/recent/`:
- Returns 200
- Returns at most 10 results
- Excludes private bookmarks
- `Access-Control-Allow-Origin: *` header is present
- Results are ordered newest-first
- The `/api/all/` endpoint does NOT set the CORS header (validates intentional scope)

**`APITagsTests`** — `GET /api/tags/`:
- Returns 200
- Each tag has `name`, `slug`, and `num_items` fields
- `num_items` counts correctly across multiple bookmarks
- Tags are sorted alphabetically

## CI Workflows

### `test.yml` — Runs on every pull request

Triggered by: any pull request, or called by `build.yml`.

Steps:
1. Checkout code
2. Install Python 3.10 dependencies (matching the production Docker image)
3. Install Node 18 npm packages (matching the production Docker image)
4. Run Django test suite
5. Run `collectstatic` to verify npm packages haven't broken static file collection

### `build.yml` — Runs on push to master

The `test` job now runs first (calling `test.yml`), and the Docker build (`container-build.yml`) only proceeds if tests pass. This prevents broken images from being pushed to the container registry.

## How to Add New Tests

1. Add test methods to the appropriate existing file, or create a new file in `bookmarks/bookmarks/tests/` or `bookmarks/api/tests/`
2. Use `django.test.TestCase` for tests that need the database; `SimpleTestCase` for tests that don't
3. Use `self.client.force_login(user)` rather than `self.client.login(...)` in view tests — it's faster and doesn't depend on password hashing
4. Use `@override_settings(...)` to test settings-dependent behaviour (e.g. Slack webhook)
5. Use `@patch(...)` from `unittest.mock` to avoid real HTTP calls in signal tests

## Detected Issues Fixed Alongside Tests

The following bugs were found while writing the tests and fixed in the same change:

- **`Bookmark.__unicode__`**: called `self.title[:40]` which raised `TypeError` when `title` is `None`. Fixed to `(self.title or '')[:40]`, and renamed to `__str__` (Python 3).
- **`importbookmarks.handle()`**: was missing the required `*args` positional parameter. Fixed to `handle(self, *args, **options)`.
- **`BookmarkTagList.get_context_data()`**: used `Tag.objects.get(slug=...)` which raised an unhandled `Tag.DoesNotExist` (500 in production) for unknown tag slugs. Fixed to `get_object_or_404(Tag, slug=...)`.
