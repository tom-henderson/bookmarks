from django.urls import include, re_path
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings
from django_common.views import LogOutRedirectView

from core.views import BookmarksList, BookmarkTagList
from core.views import BookmarkCreate, BookmarkUpdate
from core.views import Charts
from api.api import API_Bookmarks, API_RecentBookmarks, API_Tags
import django.contrib.auth.views

admin.autodiscover()

urlpatterns = [
    re_path(r'^$', BookmarksList.as_view(), name='index'),
    re_path(r'^tag/(?P<slug>[^/]+)/$', BookmarkTagList.as_view(), name='tag'),
    re_path(r'^new/$', BookmarkCreate.as_view(), name='bookmark_create'),
    re_path(r'^edit/(?P<pk>\d+)/$', BookmarkUpdate.as_view(), name='bookmark_update'),
    re_path(r'^charts/$', Charts.as_view(), name='charts'),
    re_path(r'^api/all/$', API_Bookmarks.as_view(), name='api_all'),
    re_path(r'^api/recent/$', API_RecentBookmarks.as_view(), name='api_recent'),
    re_path(r'^api/tags/$', API_Tags.as_view(), name='api_tags'),
    re_path(r'^login/$', django.contrib.auth.views.login, name='log_in'),
    re_path(r'^logout/$', LogOutRedirectView.as_view(), name='log_out'),
    re_path(r'^admin/logout/$', LogOutRedirectView.as_view()),
    re_path(r'^admin/', admin.site.urls),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
