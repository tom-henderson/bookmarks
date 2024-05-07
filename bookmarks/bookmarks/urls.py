from django.urls import include, path

from .views import BookmarksList, BookmarkTagList
from .views import BookmarkCreate, BookmarkUpdate
from .views import ModalFilterForm, ModalBookmarkUpdate, ModalBookmarkCreate
from .views import Charts

urlpatterns = [
    path('', BookmarksList.as_view(), name='index'),
    path('tag/<slug>/', BookmarkTagList.as_view(), name='tag'),
    path('new/', BookmarkCreate.as_view(), name='bookmark_create'),
    path('edit/<int:pk>/', BookmarkUpdate.as_view(), name='bookmark_update'),
    path('modal/filter', ModalFilterForm.as_view(), name='modal_filter_form'),
    path('modal/new/', ModalBookmarkCreate.as_view(), name='modal_bookmark_create'),
    path('modal/edit/<int:pk>/', ModalBookmarkUpdate.as_view(), name='modal_filter_form'),
    path('charts/', Charts.as_view(), name='charts'),
]