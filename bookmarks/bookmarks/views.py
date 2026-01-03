from django.shortcuts import render
from django.views.generic import FormView
from django.views.generic import TemplateView, ListView
from django.views.generic import CreateView, UpdateView
from django.db.models import Q, Count
from django.db.models.functions import TruncDate
from django import forms
from datetime import datetime, timedelta
from calendar import month_abbr

from .models import Bookmark
from .utils import build_activity_chart
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

        # Build activity chart data for template rendering
        context['activity_chart'] = self._build_activity_chart()

        return context

    def _build_activity_chart(self):
        """
        Build activity chart data for the last 365 days.
        Returns a dict with 'weeks' and 'month_labels' for template rendering.
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        queryset = Bookmark.objects.all()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(private=False)
        
        return build_activity_chart(queryset, start_date, end_date)


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
    template_name = 'form_view.html'
    form_class = BookmarkForm
    success_url = '/'

    def get_initial(self):
        initial = {
            'url': self.request.GET.get('url', None),
            'title': self.request.GET.get('title', None),
            'description': self.request.GET.get('description', None),
        }
        return initial


class BookmarkUpdate(LoginRequiredMixin, NextOnSuccessMixin, UpdateView):
    template_name = 'form_view.html'
    model = Bookmark
    form_class = BookmarkForm
    success_url = '/'


class Charts(TemplateView):
    template_name = 'bookmarks/charts.html'

    def get_context_data(self, **kwargs):
        context = super(Charts, self).get_context_data(**kwargs)
        
        queryset = Bookmark.objects.all()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(private=False)
        
        # Find the earliest bookmark date
        earliest_bookmark = queryset.order_by('date_added').first()
        if not earliest_bookmark:
            context['activity_years'] = []
            context['title'] = 'Activity History'
            return context
        
        # Get the year range
        earliest_year = earliest_bookmark.date_added.year
        current_year = datetime.now().year
        
        # Build one chart per calendar year
        activity_years = []
        for year in range(earliest_year, current_year + 1):
            start_date = datetime(year, 1, 1).date()
            
            # End date is either Dec 31 of that year, or today if current year
            if year == current_year:
                end_date = datetime.now().date()
            else:
                end_date = datetime(year, 12, 31).date()
            
            chart_data = build_activity_chart(queryset, start_date, end_date)
            activity_years.append({
                'year': year,
                'chart': chart_data
            })
        
        # Reverse so most recent year is first
        activity_years.reverse()
        
        context['activity_years'] = activity_years
        context['title'] = 'Activity History'
        
        return context
