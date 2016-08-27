from django.shortcuts import render
from django.views.generic import ListView

from .models import Bookmark


class BookmarksList(ListView):
    model = Bookmark
    ordering = '-date_added'
    context_object_name = 'bookmarks'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(BookmarksList, self).get_context_data(**kwargs)
        context['title'] = "Bookmarks"
        return context


class BookmarkTagList(BookmarksList):
    def get_queryset(self):
        return Bookmark.objects.filter(tags__slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        context = super(BookmarkTagList, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs.get('slug')
        return context
