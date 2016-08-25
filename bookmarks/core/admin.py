from django.contrib import admin

from .models import Bookmark


class BookmarkAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'url',
        'tags'
    ]
    ordering = ('-add_date',)
    search_fields = ('title','description','tags')

admin.site.register(Bookmark, BookmarkAdmin)
