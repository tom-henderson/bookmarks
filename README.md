# Bookmarks

## Convert imported tags to tags:

    from core.models import Bookmark

    bookmarks = Bookmark.objects.all()

    for b in bookmarks:
        for tag in b.tag_import.split(','):
            b.tags.add(tag.strip())
