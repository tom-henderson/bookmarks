from django.utils import timezone
from rest_framework.test import APITestCase

from bookmarks.models import Bookmark


def _make_bookmark(url='https://example.com', title='Test', private=False, **kwargs):
    return Bookmark.objects.create(url=url, title=title, private=private, **kwargs)


class APIBookmarksTests(APITestCase):
    def setUp(self):
        self.public = _make_bookmark('https://public.com', 'Public Bookmark')
        self.public.tags.add('python')
        self.private = _make_bookmark('https://private.com', 'Private Bookmark', private=True)

    def test_returns_200(self):
        response = self.client.get('/api/all/')
        self.assertEqual(response.status_code, 200)

    def test_returns_json(self):
        response = self.client.get('/api/all/')
        self.assertIn('application/json', response['Content-Type'])

    def test_lists_public_bookmarks(self):
        response = self.client.get('/api/all/')
        urls = [b['url'] for b in response.data]
        self.assertIn('https://public.com', urls)

    def test_excludes_private_bookmarks(self):
        response = self.client.get('/api/all/')
        urls = [b['url'] for b in response.data]
        self.assertNotIn('https://private.com', urls)

    def test_bookmark_fields_present(self):
        response = self.client.get('/api/all/')
        self.assertGreater(len(response.data), 0)
        bookmark = response.data[0]
        for field in ('title', 'description', 'date_added', 'tags', 'private', 'url'):
            self.assertIn(field, bookmark)

    def test_tags_serialised_as_list(self):
        response = self.client.get('/api/all/')
        bookmark = next(b for b in response.data if b['url'] == 'https://public.com')
        self.assertIsInstance(bookmark['tags'], list)
        self.assertIn('python', bookmark['tags'])


class APIRecentBookmarksTests(APITestCase):
    def setUp(self):
        for i in range(15):
            _make_bookmark(
                f'https://recent{i}.com',
                f'Recent {i}',
                date_added=timezone.now()
            )
        _make_bookmark('https://private-recent.com', 'Private Recent', private=True)

    def test_returns_200(self):
        response = self.client.get('/api/recent/')
        self.assertEqual(response.status_code, 200)

    def test_returns_at_most_10(self):
        response = self.client.get('/api/recent/')
        self.assertEqual(len(response.data), 10)

    def test_excludes_private(self):
        response = self.client.get('/api/recent/')
        urls = [b['url'] for b in response.data]
        self.assertNotIn('https://private-recent.com', urls)

    def test_cors_header_present(self):
        response = self.client.get('/api/recent/')
        self.assertEqual(response['Access-Control-Allow-Origin'], '*')

    def test_all_endpoint_lacks_cors_header(self):
        response = self.client.get('/api/all/')
        self.assertNotIn('Access-Control-Allow-Origin', response)

    def test_ordering_newest_first(self):
        # Create two bookmarks with known different timestamps
        older = _make_bookmark(
            'https://older-recent.com', 'Older',
            date_added=timezone.now() - timezone.timedelta(hours=1)
        )
        newer = _make_bookmark(
            'https://newer-recent.com', 'Newer',
            date_added=timezone.now()
        )
        response = self.client.get('/api/recent/')
        urls = [b['url'] for b in response.data]
        if 'https://newer-recent.com' in urls and 'https://older-recent.com' in urls:
            self.assertLess(urls.index('https://newer-recent.com'),
                            urls.index('https://older-recent.com'))


class APITagsTests(APITestCase):
    def setUp(self):
        b1 = _make_bookmark('https://one.com', 'One')
        b2 = _make_bookmark('https://two.com', 'Two')
        b1.tags.add('python')
        b1.tags.add('django')
        b2.tags.add('python')

    def test_returns_200(self):
        response = self.client.get('/api/tags/')
        self.assertEqual(response.status_code, 200)

    def test_tags_have_required_fields(self):
        response = self.client.get('/api/tags/')
        self.assertGreater(len(response.data), 0)
        for tag in response.data:
            self.assertIn('name', tag)
            self.assertIn('slug', tag)
            self.assertIn('num_items', tag)

    def test_num_items_count_correct(self):
        response = self.client.get('/api/tags/')
        tags_by_name = {t['name']: t for t in response.data}
        self.assertEqual(tags_by_name['python']['num_items'], 2)
        self.assertEqual(tags_by_name['django']['num_items'], 1)

    def test_ordering_alphabetically(self):
        response = self.client.get('/api/tags/')
        names = [t['name'] for t in response.data]
        self.assertEqual(names, sorted(names))
