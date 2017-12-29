from django.urls import include, path

from .api import API_Bookmarks, API_RecentBookmarks, API_Tags

urlpatterns = [
    path('all/', API_Bookmarks.as_view(), name='api_all'),
    path('recent/', API_RecentBookmarks.as_view(), name='api_recent'),
    path('tags/', API_Tags.as_view(), name='api_tags'),
]
