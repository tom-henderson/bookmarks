# Fixtures

## activity_demo.json

This fixture contains 50 bookmarks distributed across the last year (July 2024 - December 2025) to demonstrate the activity chart feature.

The bookmarks are distributed with varying densities to showcase all color intensity levels:
- **High activity days** (8+ bookmarks): November 5, 2025 - shows level 4 (darkest blue)
- **Medium-high activity** (5-7 bookmarks): November 15, 2025 - shows level 3
- **Medium activity** (3-4 bookmarks): November 10, December 10 - shows level 2
- **Low activity** (1-2 bookmarks): Most other dates - shows level 1
- **No activity** (0 bookmarks): Empty days - shows level 0 (light gray)

### Loading the fixture

From the workspace root:

```bash
# Activate virtual environment
source .env/bin/activate

# Load the fixture
python bookmarks/manage.py loaddata activity_demo
```

### Clearing the data

To remove the demo data and start fresh:

```bash
# Delete all bookmarks
python bookmarks/manage.py shell -c "from bookmarks.models import Bookmark; Bookmark.objects.all().delete()"
```

Or use the Django admin interface at `/admin/bookmarks/bookmark/` to manage bookmarks individually.
