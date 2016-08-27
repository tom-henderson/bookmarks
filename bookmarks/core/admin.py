from django.contrib import admin

from .models import Bookmark


class BookmarkAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'description',
        'tag_list',
        'tag_count',
        'link',
    ]
    list_filter = [
        'tags',
    ]
    ordering = ('-add_date',)
    search_fields = ('title', 'description')
    exclude = [
        'tag_import',
    ]

    def get_queryset(self, request):
        return super(BookmarkAdmin, self).get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    def tag_count(self, obj):
        return len(obj.tags.all())

    def link(self, obj):
        return u"<a href='{}'>\U0001F517</a>".format(obj.url)
    link.allow_tags = True


admin.site.register(Bookmark, BookmarkAdmin)
