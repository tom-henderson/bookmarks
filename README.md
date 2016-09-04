# Bookmarks

## Convert imported tags to tags:

    from core.models import Bookmark

    bookmarks = Bookmark.objects.all()

    for b in bookmarks:
        for tag in b.tag_import.split(','):
            b.tags.add(tag.strip())


## Bookmarklet

[Add Bookmark](javascript:(function($){url='http://127.0.0.1:8000/new/';url+='?url='+encodeURIComponent(window.location.href);url+='&title='+encodeURIComponent(document.title);url+='&description='+encodeURIComponent(''+(window.getSelection?window.getSelection():document.getSelection?document.getSelection():document.selection.createRange().text));window.open(url,"_self");})();)