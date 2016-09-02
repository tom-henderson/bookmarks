from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q

from .models import Bookmark
from taggit.models import Tag


class BookmarksList(ListView):
    model = Bookmark
    ordering = '-date_added'
    context_object_name = 'bookmarks'
    paginate_by = 20

    def get_queryset(self):
        queryset = super(BookmarksList, self).get_queryset()

        search = self.request.GET.get('search', None)

        if search:
            queryset = queryset.filter(
                Q(tags__name__contains=search) |
                Q(title__contains=search) |
                Q(description__contains=search)
            ).distinct()

        if not self.request.user.is_authenticated():
            queryset = queryset.filter(private=False)

        return queryset.prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super(BookmarksList, self).get_context_data(**kwargs)
        context['title'] = "Bookmarks"

        search = self.request.GET.get('search', None)
        if search:
            context['search'] = search

        return context


class BookmarkTagList(BookmarksList):
    def get_queryset(self):
        queryset = super(BookmarkTagList, self).get_queryset()
        return queryset.filter(tags__slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        context = super(BookmarkTagList, self).get_context_data(**kwargs)
        context['tag_filter'] = Tag.objects.get(slug=self.kwargs.get('slug'))
        return context
