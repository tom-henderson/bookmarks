from django.urls import include, path

from .views import BookmarksList, BookmarkTagList
from .views import BookmarkCreate, BookmarkUpdate
from .views import Charts

urlpatterns = [
    path('', BookmarksList.as_view(), name='index'),
    path('tag/<slug>/', BookmarkTagList.as_view(), name='tag'),
    path('new/', BookmarkCreate.as_view(), name='bookmark_create'),
    path('edit/<int:pk>/', BookmarkUpdate.as_view(), name='bookmark_update'),
    path('charts/', Charts.as_view(), name='charts'),
]
