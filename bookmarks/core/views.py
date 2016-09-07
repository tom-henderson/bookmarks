from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import CreateView, UpdateView
from django.db.models import Q
from django import forms

from .models import Bookmark
from taggit.models import Tag
from common.views import LoginRequiredMixin
from common.forms import BootStrapForm


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
                Q(tags__name__icontains=search) |
                Q(title__icontains=search) |
                Q(description__icontains=search)
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
        tag = Tag.objects.get(slug=self.kwargs.get('slug'))

        context = super(BookmarkTagList, self).get_context_data(**kwargs)
        context['title'] = "Bookmarks - {}".format(tag.name)
        context['tag_filter'] = tag.slug
        return context


class BookmarkForm(BootStrapForm):
    class Meta:
        model = Bookmark
        fields = [
            'title',
            'description',
            'url',
            'tags',
        ]

    def __init__(self, *args, **kwargs):
        super(BookmarkForm, self).__init__(*args, **kwargs)

        self.fields['tags'].widget.attrs['data-role'] = 'tagsinput'


class BookmarkCreate(LoginRequiredMixin, CreateView):
    template_name = 'form_view.html'
    form_class = BookmarkForm
    success_url = "/"

    def get_initial(self):
        initial = {
            'url': self.request.GET.get('url', None),
            'title': self.request.GET.get('title', None),
            'description': self.request.GET.get('description', None),
        }
        return initial
