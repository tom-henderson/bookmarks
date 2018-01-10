from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookmarks', '0004_auto_20160901_2322'),
    ]

    operations = [
        migrations.RunSQL("DROP TABLE bookmarks_bookmark;"),
        migrations.RunSQL("ALTER TABLE core_bookmark RENAME TO bookmarks_bookmark;"),
        migrations.RunSQL("UPDATE django_content_type SET app_label='bookmarks' WHERE app_label='core';"),
    ]