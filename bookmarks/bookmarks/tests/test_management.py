import json
import tempfile
import os

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from bookmarks.models import Bookmark


SAMPLE_DATA = [
    {
        'title': 'First Bookmark',
        'description': 'First description',
        'date_added': '2024-01-15T10:00:00',
        'private': False,
        'url': 'https://first.example.com',
        'tags': ['python', 'web'],
    },
    {
        'title': 'Second Bookmark',
        'description': 'Second description',
        'date_added': '2024-02-20T12:00:00',
        'private': True,
        'url': 'https://second.example.com',
        'tags': ['django'],
    },
]


class ImportBookmarksCommandTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self._tmp.close()

    def tearDown(self):
        os.unlink(self._tmp.name)

    def _write(self, data):
        with open(self._tmp.name, 'w') as f:
            json.dump(data, f)
        return self._tmp.name

    def test_import_creates_bookmarks(self):
        call_command('importbookmarks', self._write(SAMPLE_DATA))
        self.assertEqual(Bookmark.objects.count(), 2)

    def test_import_sets_url(self):
        call_command('importbookmarks', self._write(SAMPLE_DATA[:1]))
        self.assertEqual(Bookmark.objects.get().url, 'https://first.example.com')

    def test_import_sets_title(self):
        call_command('importbookmarks', self._write(SAMPLE_DATA[:1]))
        self.assertEqual(Bookmark.objects.get().title, 'First Bookmark')

    def test_import_sets_description(self):
        call_command('importbookmarks', self._write(SAMPLE_DATA[:1]))
        self.assertEqual(Bookmark.objects.get().description, 'First description')

    def test_import_sets_private(self):
        call_command('importbookmarks', self._write(SAMPLE_DATA))
        self.assertFalse(Bookmark.objects.get(url='https://first.example.com').private)
        self.assertTrue(Bookmark.objects.get(url='https://second.example.com').private)

    def test_import_sets_tags(self):
        call_command('importbookmarks', self._write(SAMPLE_DATA[:1]))
        tags = Bookmark.objects.get().tags.names()
        self.assertIn('python', tags)
        self.assertIn('web', tags)

    def test_import_empty_array_creates_nothing(self):
        call_command('importbookmarks', self._write([]))
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_import_nonexistent_file_raises(self):
        with self.assertRaises((FileNotFoundError, CommandError)):
            call_command('importbookmarks', '/nonexistent/path/file.json')
