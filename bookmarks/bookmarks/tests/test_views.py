import os
from datetime import timedelta
from pathlib import Path

from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from unittest import skipIf

from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.utils import timezone

from bookmarks.models import Bookmark


def _make_bookmark(url='https://example.com', title='Test', private=False, **kwargs):
    return Bookmark.objects.create(url=url, title=title, private=private, **kwargs)


class BookmarksListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('testuser', 'test@example.com', 'password')
        self.public1 = _make_bookmark('https://pub1.com', 'Public One')
        self.public2 = _make_bookmark('https://pub2.com', 'Public Two')
        self.public3 = _make_bookmark('https://pub3.com', 'Searchable description bookmark',
                                      description='unique_desc_xyz')
        self.private = _make_bookmark('https://priv.com', 'Private One', private=True)
        self.public1.tags.add('python', 'django')

    def test_anonymous_sees_public_only(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        bookmarks = list(response.context['bookmarks'])
        self.assertIn(self.public1, bookmarks)
        self.assertNotIn(self.private, bookmarks)

    def test_authenticated_sees_private(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('index'))
        bookmarks = list(response.context['bookmarks'])
        self.assertIn(self.private, bookmarks)
        self.assertIn(self.public1, bookmarks)

    def test_status_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'bookmarks/bookmark_list.html')

    def test_context_title(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['title'], 'Bookmarks')

    def test_search_by_title(self):
        response = self.client.get(reverse('index') + '?search=Public+One')
        bookmarks = list(response.context['bookmarks'])
        self.assertIn(self.public1, bookmarks)
        self.assertNotIn(self.public2, bookmarks)

    def test_search_by_description(self):
        response = self.client.get(reverse('index') + '?search=unique_desc_xyz')
        bookmarks = list(response.context['bookmarks'])
        self.assertIn(self.public3, bookmarks)
        self.assertNotIn(self.public1, bookmarks)

    def test_search_by_tag(self):
        response = self.client.get(reverse('index') + '?search=python')
        bookmarks = list(response.context['bookmarks'])
        self.assertIn(self.public1, bookmarks)
        self.assertNotIn(self.public2, bookmarks)

    def test_date_filter_from_future_returns_empty(self):
        future = (timezone.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        response = self.client.get(reverse('index') + f'?date_added_from={future}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['bookmarks']), 0)

    def test_date_filter_to_past_returns_empty(self):
        response = self.client.get(reverse('index') + '?date_added_to=2000-01-01')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['bookmarks']), 0)

    def test_pagination_20_per_page(self):
        for i in range(20):
            _make_bookmark(f'https://extra{i}.com', f'Extra {i}')
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context['bookmarks']), 20)

    def test_pagination_page_2(self):
        for i in range(20):
            _make_bookmark(f'https://extra{i}.com', f'Extra {i}')
        # 3 public from setUp + 20 new = 23 public; page 2 should have 3
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['bookmarks']), 3)

    def test_activity_chart_in_context(self):
        response = self.client.get(reverse('index'))
        chart = response.context['activity_chart']
        self.assertIn('weeks', chart)
        self.assertIn('month_labels', chart)

    def test_ordering_newest_first(self):
        older = _make_bookmark('https://older.com', 'Older',
                               date_added=timezone.now() - timedelta(days=10))
        newer = _make_bookmark('https://newer.com', 'Newer',
                               date_added=timezone.now())
        response = self.client.get(reverse('index'))
        bookmarks = list(response.context['bookmarks'])
        newer_idx = next(i for i, b in enumerate(bookmarks) if b.pk == newer.pk)
        older_idx = next(i for i, b in enumerate(bookmarks) if b.pk == older.pk)
        self.assertLess(newer_idx, older_idx)

    def test_search_context_set_when_present(self):
        response = self.client.get(reverse('index') + '?search=python')
        self.assertEqual(response.context.get('search'), 'python')

    def test_search_context_not_set_when_absent(self):
        response = self.client.get(reverse('index'))
        self.assertNotIn('search', response.context)


class BookmarkTagListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('testuser', 'test@example.com', 'password')
        self.python_bookmark = _make_bookmark('https://python.com', 'Python Site')
        self.django_bookmark = _make_bookmark('https://django.com', 'Django Site')
        self.private_tagged = _make_bookmark('https://priv.com', 'Private', private=True)
        self.python_bookmark.tags.add('python')
        self.django_bookmark.tags.add('django')
        self.private_tagged.tags.add('python')

    def test_filters_by_tag(self):
        response = self.client.get(reverse('tag', kwargs={'slug': 'python'}))
        self.assertEqual(response.status_code, 200)
        bookmarks = list(response.context['bookmarks'])
        self.assertIn(self.python_bookmark, bookmarks)
        self.assertNotIn(self.django_bookmark, bookmarks)

    def test_title_includes_tag_name(self):
        response = self.client.get(reverse('tag', kwargs={'slug': 'python'}))
        self.assertIn('python', response.context['title'].lower())

    def test_404_for_nonexistent_tag(self):
        response = self.client.get(reverse('tag', kwargs={'slug': 'nonexistent-xyz'}))
        self.assertEqual(response.status_code, 404)

    def test_excludes_private_for_anonymous(self):
        response = self.client.get(reverse('tag', kwargs={'slug': 'python'}))
        bookmarks = list(response.context['bookmarks'])
        self.assertNotIn(self.private_tagged, bookmarks)

    def test_includes_private_for_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('tag', kwargs={'slug': 'python'}))
        bookmarks = list(response.context['bookmarks'])
        self.assertIn(self.private_tagged, bookmarks)


class BookmarkCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')

    def test_login_required_redirect(self):
        response = self.client.get(reverse('bookmark_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_authenticated_get_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bookmark_create'))
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bookmark_create'))
        self.assertTemplateUsed(response, 'form_view.html')

    def test_initial_url_from_get_param(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bookmark_create') + '?url=https://prefill.com')
        form = response.context['form']
        self.assertEqual(form.initial.get('url'), 'https://prefill.com')

    def test_initial_title_from_get_param(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bookmark_create') + '?title=Prefilled+Title')
        form = response.context['form']
        self.assertEqual(form.initial.get('title'), 'Prefilled Title')

    def test_initial_description_from_get_param(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bookmark_create') + '?description=Some+desc')
        form = response.context['form']
        self.assertEqual(form.initial.get('description'), 'Some desc')

    def test_post_creates_bookmark(self):
        self.client.force_login(self.user)
        count_before = Bookmark.objects.count()
        response = self.client.post(reverse('bookmark_create'), {
            'url': 'https://new.example.com',
            'title': 'New Bookmark',
            'tags': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Bookmark.objects.count(), count_before + 1)

    def test_post_invalid_url_shows_errors(self):
        self.client.force_login(self.user)
        count_before = Bookmark.objects.count()
        response = self.client.post(reverse('bookmark_create'), {
            'url': 'not-a-url',
            'title': 'Bad URL',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Bookmark.objects.count(), count_before)

    def test_post_missing_url_shows_errors(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('bookmark_create'), {'title': 'No URL'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('url', response.context['form'].errors)


class BookmarkUpdateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')
        self.bookmark = _make_bookmark('https://edit.com', 'Original Title')

    def test_login_required_redirect(self):
        response = self.client.get(reverse('bookmark_update', kwargs={'pk': self.bookmark.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_authenticated_get_returns_200(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bookmark_update', kwargs={'pk': self.bookmark.pk}))
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bookmark_update', kwargs={'pk': self.bookmark.pk}))
        self.assertTemplateUsed(response, 'form_view.html')

    def test_post_updates_bookmark(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('bookmark_update', kwargs={'pk': self.bookmark.pk}),
            {'url': 'https://edit.com', 'title': 'Updated Title', 'tags': ''}
        )
        self.assertEqual(response.status_code, 302)
        self.bookmark.refresh_from_db()
        self.assertEqual(self.bookmark.title, 'Updated Title')

    def test_404_for_nonexistent_pk(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('bookmark_update', kwargs={'pk': 99999}))
        self.assertEqual(response.status_code, 404)


class ChartsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')

    def test_renders_200(self):
        response = self.client.get(reverse('charts'))
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        response = self.client.get(reverse('charts'))
        self.assertTemplateUsed(response, 'bookmarks/charts.html')

    def test_no_bookmarks_returns_empty_list(self):
        response = self.client.get(reverse('charts'))
        self.assertEqual(response.context['activity_years'], [])

    def test_activity_years_built_per_year(self):
        now = timezone.now()
        two_years_ago = now - timedelta(days=730)
        Bookmark.objects.create(url='https://old.com', date_added=two_years_ago)
        Bookmark.objects.create(url='https://new.com', date_added=now)
        response = self.client.get(reverse('charts'))
        years = response.context['activity_years']
        self.assertGreaterEqual(len(years), 2)
        for entry in years:
            self.assertIn('year', entry)
            self.assertIn('chart', entry)

    def test_context_title(self):
        response = self.client.get(reverse('charts'))
        self.assertEqual(response.context['title'], 'Activity History')

    def test_anonymous_excludes_private_from_charts(self):
        # Private bookmark should not count in anonymous chart
        private = _make_bookmark('https://priv.com', 'Private', private=True)
        response = self.client.get(reverse('charts'))
        # No bookmarks visible → empty list
        self.assertEqual(response.context['activity_years'], [])

    def test_authenticated_includes_private_in_charts(self):
        self.client.force_login(self.user)
        _make_bookmark('https://priv.com', 'Private', private=True)
        response = self.client.get(reverse('charts'))
        self.assertGreater(len(response.context['activity_years']), 0)

    def test_older_year_bookmark_shows_data_in_chart(self):
        # Regression test: bookmarks stored with the old ISO 8601 T-separator
        # format ('2019-06-15T12:00:00+00:00') must appear in the chart.
        # Django's typecast_timestamp() only handles space-separated strings;
        # the T-format silently produced NULL from TruncDate, hiding all
        # pre-2022 history.  Store directly via .update() to bypass the ORM's
        # format normalisation and reproduce the exact historical storage format.
        self.client.force_login(self.user)
        bm = _make_bookmark('https://old.com', 'Old Bookmark')
        Bookmark.objects.filter(pk=bm.pk).update(date_added='2019-06-15T12:00:00+00:00')
        response = self.client.get(reverse('charts'))
        years = {entry['year']: entry for entry in response.context['activity_years']}
        self.assertIn(2019, years)
        days_with_data = [
            day
            for week in years[2019]['chart']['weeks']
            for day in week
            if day.get('count', 0) > 0
        ]
        self.assertGreater(len(days_with_data), 0)


class AuthViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password')

    def test_login_page_get(self):
        response = self.client.get(reverse('log_in'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_valid_credentials(self):
        response = self.client.post(reverse('log_in'), {
            'username': 'testuser',
            'password': 'password',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_post_invalid_credentials(self):
        response = self.client.post(reverse('log_in'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('log_out'))
        self.assertEqual(response.status_code, 302)


class AppVersionViewTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'superuser', 'super@example.com', 'password'
        )
        self.staff_user = User.objects.create_user(
            'staffuser', 'staff@example.com', 'password', is_staff=True
        )
        self.regular_user = User.objects.create_user(
            'regularuser', 'regular@example.com', 'password'
        )

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(reverse('app_version'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_superuser_returns_200(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('app_version'))
        self.assertEqual(response.status_code, 200)

    def test_regular_user_returns_403(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse('app_version'))
        self.assertEqual(response.status_code, 403)

    def test_staff_non_superuser_returns_403(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(reverse('app_version'))
        self.assertEqual(response.status_code, 403)

    def test_correct_template_used(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('app_version'))
        self.assertTemplateUsed(response, 'bookmarks/app_version.html')

    def test_context_contains_build_info(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('app_version'))
        self.assertIn('build_version', response.context)
        self.assertIn('build_date', response.context)
        self.assertIn('build_commit', response.context)

    def test_build_version_defaults_to_dev(self):
        os.environ.pop('BUILD_VERSION', None)
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('app_version'))
        self.assertEqual(response.context['build_version'], 'dev')

    def test_build_version_reads_env_var(self):
        os.environ['BUILD_VERSION'] = '2.3.4'
        try:
            self.client.force_login(self.superuser)
            response = self.client.get(reverse('app_version'))
            self.assertEqual(response.context['build_version'], '2.3.4')
        finally:
            os.environ.pop('BUILD_VERSION', None)

    def test_context_contains_packages_list(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('app_version'))
        self.assertIn('packages', response.context)
        self.assertIsInstance(response.context['packages'], list)

    def test_packages_have_required_keys(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('app_version'))
        packages = response.context['packages']
        if packages:
            pkg = packages[0]
            self.assertIn('name', pkg)
            self.assertIn('required', pkg)
            self.assertIn('installed', pkg)

    def test_context_title(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse('app_version'))
        self.assertEqual(response.context['title'], 'App Version')


NODE_MODULES = Path(__file__).parents[3] / 'node_modules'


@skipIf(not os.path.isdir(NODE_MODULES), 'node_modules not installed; skipping static file tests')
class StaticFileFinderTests(SimpleTestCase):
    """
    Verify that npm packages expose the files referenced in NPM_FILE_PATTERNS.
    These tests catch path changes caused by JavaScript package upgrades.
    """
    def _assert_static_file_found(self, path):
        result = finders.find(f'npm/{path}')
        self.assertIsNotNone(result, f'Static file not found: npm/{path}')

    def test_jquery_found(self):
        self._assert_static_file_found('jquery/dist/jquery.min.js')

    def test_bootstrap_css_found(self):
        self._assert_static_file_found('bootstrap/dist/css/bootstrap.min.css')

    def test_bootstrap_js_found(self):
        self._assert_static_file_found('bootstrap/dist/js/bootstrap.min.js')

    def test_bootswatch_slate_found(self):
        self._assert_static_file_found('bootswatch/slate/bootstrap.min.css')

    def test_typeahead_found(self):
        self._assert_static_file_found('typeahead.js/dist/typeahead.bundle.min.js')

    def test_font_awesome_css_found(self):
        self._assert_static_file_found('font-awesome/css/font-awesome.min.css')

    def test_bootstrap_datepicker_found(self):
        self._assert_static_file_found('bootstrap-datepicker/dist/css/bootstrap-datepicker.min.css')

    def test_bootstrap_tokenfield_found(self):
        self._assert_static_file_found('bootstrap-tokenfield/dist/bootstrap-tokenfield.min.js')
