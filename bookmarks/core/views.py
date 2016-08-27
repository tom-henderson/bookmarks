from django.shortcuts import render
from django.views.generic import ListView

from .models import Bookmark


class BookmarksList(ListView):
    queryset = Bookmark.objects.all().order_by('-add_date')
    # template_name = 'core/bookmarks.html'
    context_object_name = 'bookmarks'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(BookmarksList, self).get_context_data(**kwargs)
        context['title'] = "Bookmarks"
        return context
