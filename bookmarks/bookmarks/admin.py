from django.contrib import admin
from django.utils.html import mark_safe

from taggit_helpers.admin import TaggitCounter, TaggitListFilter

from .models import Bookmark


class BookmarkAdmin(TaggitCounter, admin.ModelAdmin):
    list_display = [
        'title',
        'description',
        'date_added',
        'tag_list',
        'taggit_counter',
        'link',
    ]
    list_filter = [
        'date_added',
        TaggitListFilter
    ]
    ordering = ('-date_added',)
    search_fields = ('title', 'description')
    exclude = (
        'date_added',
    )

    def get_queryset(self, request):
        return super(BookmarkAdmin, self).get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    def link(self, obj):
        return mark_safe(f"<a href='{obj.url}'>\U0001F517</a>")


admin.site.register(Bookmark, BookmarkAdmin)
