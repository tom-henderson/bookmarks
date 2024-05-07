from django.shortcuts import render
from django.views.generic import FormView
from django.views.generic import TemplateView, ListView
from django.views.generic import CreateView, UpdateView
from django.db.models import Q
from django import forms

from .models import Bookmark
from taggit.models import Tag
from django_common.views import LoginRequiredMixin
from django_common.forms import BootStrapForm, NextOnSuccessMixin


class BookmarksList(ListView):
    model = Bookmark
    ordering = '-date_added'
    context_object_name = 'bookmarks'
    paginate_by = 20

    def get_queryset(self):
        queryset = super(BookmarksList, self).get_queryset()

        search = self.request.GET.get('search', None)
        date_added_from = self.request.GET.get('date_added_from', None)
        date_added_to = self.request.GET.get('date_added_to', None)

        if search:
            queryset = queryset.filter(
                Q(tags__name__icontains=search) |
                Q(title__icontains=search) |
                Q(description__icontains=search)
            ).distinct()

        if date_added_from:
            queryset = queryset.filter(date_added__gte=date_added_from)

        if date_added_to:
            queryset = queryset.filter(date_added__lte=date_added_to)

        if not self.request.user.is_authenticated:
            queryset = queryset.filter(private=False)

        return queryset.prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super(BookmarksList, self).get_context_data(**kwargs)
        context['title'] = "Bookmarks"
        context['date_added_from'] = self.request.GET.get('date_added_from', None)
        context['date_added_to'] = self.request.GET.get('date_added_to', None)

        # We only add search to context if it exists
        # because otherwise using {% if search|lower in tag.name %}
        # returns true for all tags.
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
        # Use the bootstrap-tagsinput field:
        self.fields['tags'].widget.attrs['data-role'] = 'tagsinput'


class BookmarkCreate(LoginRequiredMixin, NextOnSuccessMixin, CreateView):
    form_class = BookmarkForm
    success_url = '/'

    def get_template_names(self):
        if self.request.GET.get('modal'):
            return ['form_modal.html']
        else:
            return ['form_view.html']

    def get_initial(self):
        initial = {
            'url': self.request.GET.get('url', None),
            'title': self.request.GET.get('title', None),
            'description': self.request.GET.get('description', None),
        }
        return initial


class BookmarkUpdate(LoginRequiredMixin, NextOnSuccessMixin, UpdateView):
    model = Bookmark
    form_class = BookmarkForm
    success_url = '/'
    
    def get_template_names(self):
        if self.request.GET.get('modal'):
            return ['form_modal.html']
        else:
            return ['form_view.html']


class Charts(TemplateView):
    template_name = 'bookmarks/charts.html'


class ModalFilterForm(TemplateView):
    template_name = 'bookmarks/filter_form.html'
    
    def get_context_data(self, **kwargs):
        context = super(ModalFilterForm, self).get_context_data(**kwargs)
        context['date_added_from'] = self.request.GET.get('date_added_from', None)
        context['date_added_to'] = self.request.GET.get('date_added_to', None)
        return context

