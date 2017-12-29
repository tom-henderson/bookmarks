from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django_common.views import LogOutRedirectView

from bookmarks.views import BookmarksList, BookmarkTagList
from bookmarks.views import BookmarkCreate, BookmarkUpdate
from bookmarks.views import Charts
from api.api import API_Bookmarks, API_RecentBookmarks, API_Tags
import django.contrib.auth.views

admin.autodiscover()

urlpatterns = [
    path('', BookmarksList.as_view(), name='index'),
    path('tag/<slug>/', BookmarkTagList.as_view(), name='tag'),
    path('new/', BookmarkCreate.as_view(), name='bookmark_create'),
    path('edit/<int:pk>/', BookmarkUpdate.as_view(), name='bookmark_update'),
    path('charts/', Charts.as_view(), name='charts'),
    path('api/all/', API_Bookmarks.as_view(), name='api_all'),
    path('api/recent/', API_RecentBookmarks.as_view(), name='api_recent'),
    path('api/tags/', API_Tags.as_view(), name='api_tags'),
    path('login/', django.contrib.auth.views.login, name='log_in'),
    path('logout/', LogOutRedirectView.as_view(), name='log_out'),
    path('admin/logout/', LogOutRedirectView.as_view()),
    path('admin/', admin.site.urls),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
