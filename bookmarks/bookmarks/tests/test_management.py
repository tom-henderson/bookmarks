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


def _write_json_file(data):
    """Write data to a temp file and return its path. Caller must delete."""
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    json.dump(data, f)
    f.close()
    return f.name


class ImportBookmarksCommandTests(TestCase):
    def test_import_creates_bookmarks(self):
        path = _write_json_file(SAMPLE_DATA)
        try:
            call_command('importbookmarks', path)
        finally:
            os.unlink(path)
        self.assertEqual(Bookmark.objects.count(), 2)

    def test_import_sets_url(self):
        path = _write_json_file(SAMPLE_DATA[:1])
        try:
            call_command('importbookmarks', path)
        finally:
            os.unlink(path)
        b = Bookmark.objects.get()
        self.assertEqual(b.url, 'https://first.example.com')

    def test_import_sets_title(self):
        path = _write_json_file(SAMPLE_DATA[:1])
        try:
            call_command('importbookmarks', path)
        finally:
            os.unlink(path)
        b = Bookmark.objects.get()
        self.assertEqual(b.title, 'First Bookmark')

    def test_import_sets_description(self):
        path = _write_json_file(SAMPLE_DATA[:1])
        try:
            call_command('importbookmarks', path)
        finally:
            os.unlink(path)
        b = Bookmark.objects.get()
        self.assertEqual(b.description, 'First description')

    def test_import_sets_private(self):
        path = _write_json_file(SAMPLE_DATA)
        try:
            call_command('importbookmarks', path)
        finally:
            os.unlink(path)
        public = Bookmark.objects.get(url='https://first.example.com')
        private = Bookmark.objects.get(url='https://second.example.com')
        self.assertFalse(public.private)
        self.assertTrue(private.private)

    def test_import_sets_tags(self):
        path = _write_json_file(SAMPLE_DATA[:1])
        try:
            call_command('importbookmarks', path)
        finally:
            os.unlink(path)
        b = Bookmark.objects.get()
        self.assertIn('python', b.tags.names())
        self.assertIn('web', b.tags.names())

    def test_import_empty_array_creates_nothing(self):
        path = _write_json_file([])
        try:
            call_command('importbookmarks', path)
        finally:
            os.unlink(path)
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_import_nonexistent_file_raises(self):
        with self.assertRaises((FileNotFoundError, CommandError)):
            call_command('importbookmarks', '/nonexistent/path/file.json')
