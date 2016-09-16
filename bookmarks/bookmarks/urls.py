from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib import admin
from django.conf import settings

import views
from core.views import BookmarksList, BookmarkTagList
from core.views import BookmarkCreate
from core.views import Charts
from api.api import API_Bookmarks, API_RecentBookmarks, API_Tags
import django.contrib.auth.views

admin.autodiscover()

urlpatterns = [
    url(r'^$', BookmarksList.as_view(), name='index'),
    url(r'^tag/(?P<slug>[^/]+)/$', BookmarkTagList.as_view(), name='tag'),
    url(r'^new/$', BookmarkCreate.as_view(), name='bookmark_create'),
    url(r'^charts/$', Charts.as_view(), name='charts'),
    url(r'^api/all/$', API_Bookmarks.as_view(), name='api_all'),
    url(r'^api/recent/$', API_RecentBookmarks.as_view(), name='api_recent'),
    url(r'^api/tags/$', API_Tags.as_view(), name='api_tags'),
    url(r'^login/$', django.contrib.auth.views.login, name='log_in'),
    url(r'^logout/$', views.log_out, name='log_out'),
    url(r'^admin/logout/$', views.log_out),
    url(r'^admin/', include(admin.site.urls)),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
