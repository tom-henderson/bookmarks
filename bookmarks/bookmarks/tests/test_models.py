from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.utils import timezone

from bookmarks.models import Bookmark


class BookmarkModelTests(TestCase):
    def test_create_with_required_fields(self):
        b = Bookmark.objects.create(url='https://example.com')
        self.assertIsNotNone(b.pk)

    def test_title_optional(self):
        b = Bookmark.objects.create(url='https://example.com', title=None)
        self.assertIsNone(b.title)

    def test_description_optional(self):
        b = Bookmark.objects.create(url='https://example.com', description=None)
        self.assertIsNone(b.description)

    def test_default_private_false(self):
        b = Bookmark.objects.create(url='https://example.com')
        self.assertFalse(b.private)

    def test_private_can_be_true(self):
        b = Bookmark.objects.create(url='https://example.com', private=True)
        self.assertTrue(b.private)

    def test_date_added_defaults_to_now(self):
        before = timezone.now()
        b = Bookmark.objects.create(url='https://example.com')
        after = timezone.now()
        self.assertGreaterEqual(b.date_added, before)
        self.assertLessEqual(b.date_added, after)

    def test_url_accepts_500_chars(self):
        long_url = 'https://example.com/' + 'a' * 480
        self.assertEqual(len(long_url), 500)
        b = Bookmark.objects.create(url=long_url)
        self.assertIsNotNone(b.pk)

    def test_title_accepts_200_chars(self):
        b = Bookmark.objects.create(url='https://example.com', title='x' * 200)
        self.assertEqual(len(b.title), 200)

    def test_tags_can_be_added(self):
        b = Bookmark.objects.create(url='https://example.com')
        b.tags.add('python', 'django')
        self.assertEqual(b.tags.count(), 2)
        self.assertIn('python', b.tags.names())
        self.assertIn('django', b.tags.names())

    def test_tags_case_insensitive(self):
        # TAGGIT_CASE_INSENSITIVE=True means "Python" and "python" are the same tag
        b = Bookmark.objects.create(url='https://example.com')
        b.tags.add('Python')
        b.tags.add('python')
        self.assertEqual(b.tags.count(), 1)

    def test_str_representation_with_title(self):
        b = Bookmark.objects.create(url='https://example.com', title='My Bookmark')
        result = str(b)
        self.assertIn('My Bookmark', result)

    def test_str_representation_with_none_title(self):
        b = Bookmark.objects.create(url='https://example.com', title=None)
        # Should not raise TypeError — fixed in models.py
        result = str(b)
        self.assertIsInstance(result, str)


class BookmarkSignalTests(TestCase):
    def test_no_notification_when_no_webhook_url(self):
        with patch('bookmarks.models.requests.post') as mock_post:
            Bookmark.objects.create(url='https://example.com', title='Test')
            mock_post.assert_not_called()

    @override_settings(SLACK_WEBHOOK_URL='https://hooks.slack.com/test')
    def test_slack_notification_sent_on_create(self):
        with patch('bookmarks.models.requests.post') as mock_post:
            Bookmark.objects.create(url='https://example.com', title='Test')
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            self.assertEqual(call_args[0][0], 'https://hooks.slack.com/test')
            payload = call_args[1]['json']
            self.assertIn('https://example.com', payload['text'])

    @override_settings(SLACK_WEBHOOK_URL='https://hooks.slack.com/test')
    def test_no_notification_on_update(self):
        with patch('bookmarks.models.requests.post') as mock_post:
            b = Bookmark.objects.create(url='https://example.com', title='Test')
            b.title = 'Updated'
            b.save()
            # Only called once (on create), not on update
            mock_post.assert_called_once()

    @override_settings(SLACK_WEBHOOK_URL='https://hooks.slack.com/test')
    def test_notification_failure_does_not_crash(self):
        with patch('bookmarks.models.requests.post', side_effect=Exception('network error')):
            # Should not raise — signal silences exceptions
            Bookmark.objects.create(url='https://example.com', title='Test')
