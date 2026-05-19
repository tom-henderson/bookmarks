from django.db import migrations


def fix_sqlite_schema_and_normalize_dates(apps, schema_editor):
    if schema_editor.connection.vendor != 'sqlite':
        return

    # auth_group.id has no PRIMARY KEY or UNIQUE declaration in this database
    # (created by an older Django version).  SQLite's foreign_key_check requires
    # the referenced column to carry a PK or UNIQUE constraint; without it every
    # migration that exits cleanly raises "foreign key mismatch".  A UNIQUE index
    # satisfies that requirement without requiring a full table rebuild.
    schema_editor.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS bookmarks_auth_group_id_uniq "
        "ON auth_group (id)"
    )

    # Old bookmarks were stored with ISO 8601 T-separator and +00:00 timezone
    # suffix (e.g. '2005-09-08T04:08:32+00:00').  Django's SQLite backend
    # typecast_timestamp() only handles space-separated strings; the T-format
    # triggers a ValueError that is silently swallowed, causing TruncDate and
    # __date lookups to return NULL for every affected row and making all
    # pre-2022 history invisible in the charts view.
    schema_editor.execute(
        "UPDATE bookmarks_bookmark "
        "SET date_added = REPLACE(REPLACE(date_added, 'T', ' '), '+00:00', '') "
        "WHERE date_added LIKE '%T%'"
    )


class Migration(migrations.Migration):
    dependencies = [
        ('bookmarks', '0004_auto_20160901_2322'),
    ]
    operations = [
        migrations.RunPython(
            fix_sqlite_schema_and_normalize_dates,
            migrations.RunPython.noop,
        ),
    ]
