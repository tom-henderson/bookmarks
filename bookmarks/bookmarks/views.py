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
        Build activity chart data structure for server-side template rendering.
        Returns a dict with 'weeks' (list of weeks, each containing day dicts) 
        and 'month_labels' (list of month label dicts with offset positions).
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=365)
        
        queryset = Bookmark.objects.all()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(private=False)
        
        # Query database for bookmark counts by date
        activity_data = queryset.filter(
            date_added__date__gte=start_date,
            date_added__date__lte=end_date
        ).annotate(
            date=TruncDate('date_added')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Convert to dict for O(1) lookup
        activity_dict = {str(item['date']): item['count'] for item in activity_data}
        
        # Build grid of all dates in the last year
        activity_grid = []
        current_date = start_date
        while current_date <= end_date:
            count = activity_dict.get(str(current_date), 0)
            activity_grid.append({
                'date': str(current_date),
                'count': count,
                'day_of_week': current_date.weekday()  # 0=Monday, 6=Sunday
            })
            current_date += timedelta(days=1)
        
        # Build weeks and month labels
        weeks = []
        current_week = []
        month_labels = []
        week_index = 0
        current_month = None
        
        # Adjust first day to start_date's day of week (convert to 0=Sunday)
        first_day_of_week = (activity_grid[0]['day_of_week'] + 1) % 7  # Convert Mon=0 to Sun=0
        
        # Add empty cells for the first week to align with Sunday
        for i in range(first_day_of_week):
            current_week.append({'date': None, 'count': 0, 'level': 0, 'title': None})
        
        # Process each day
        for index, day_data in enumerate(activity_grid):
            date_obj = datetime.strptime(day_data['date'], '%Y-%m-%d').date()
            day_of_week = (day_data['day_of_week'] + 1) % 7  # Convert to 0=Sunday
            count = day_data['count']
            month = date_obj.month
            
            # Track month changes for labels (on Sundays)
            if day_of_week == 0 and month != current_month:
                month_labels.append({
                    'week_index': week_index,
                    'offset': week_index * 14 - 14,  # 11px width + 3px gap
                    'label': month_abbr[month]
                })
                current_month = month
            
            # Determine color level (0-4) based on bookmark count
            level = 0
            if count > 0:
                level = 1
            if count >= 3:
                level = 2
            if count >= 5:
                level = 3
            if count >= 8:
                level = 4
            
            title = '{}: {} bookmark{}'.format(
                day_data['date'],
                count,
                's' if count != 1 else ''
            )
            
            current_week.append({
                'date': day_data['date'],  # Always include date for real days
                'count': count,
                'level': level,
                'title': title,
                'clickable': count > 0  # Only days with bookmarks are clickable
            })
            
            # Start new week on Saturday (day 6) or at end of data
            if day_of_week == 6 or index == len(activity_grid) - 1:
                weeks.append(current_week)
                current_week = []
                week_index += 1
        
        return {
            'weeks': weeks,
            'month_labels': month_labels
        }


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
