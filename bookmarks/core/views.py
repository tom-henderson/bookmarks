from django.shortcuts import render
from django.views.generic import ListView

from .models import Bookmark


class BookmarksList(ListView):
    model = Bookmark
    ordering = '-date_added'
    context_object_name = 'bookmarks'
    paginate_by = 20

    def get_queryset(self):
        queryset = super(BookmarksList, self).get_queryset()

        if not self.request.user.is_authenticated():
            queryset = queryset.filter(private=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(BookmarksList, self).get_context_data(**kwargs)
        context['title'] = "Bookmarks"
        return context


class BookmarkTagList(BookmarksList):
    def get_queryset(self):
        queryset = super(BookmarkTagList, self).get_queryset()
        return queryset.filter(tags__slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        context = super(BookmarkTagList, self).get_context_data(**kwargs)
        context['slug'] = self.kwargs.get('slug')
        return context
