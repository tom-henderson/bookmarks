import calendar
from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone

from bookmarks.models import Bookmark
from bookmarks.utils import build_activity_chart


def _all_real_days(result):
    """Return all non-padding day dicts from the chart result."""
    return [
        day
        for week in result['weeks']
        for day in week
        if day.get('date') is not None
    ]


class BuildActivityChartTests(TestCase):
    def setUp(self):
        self.start = date(2024, 1, 1)
        self.qs = Bookmark.objects.all()

    def test_returns_expected_keys(self):
        result = build_activity_chart(self.qs, self.start)
        self.assertIn('weeks', result)
        self.assertIn('month_labels', result)

    def test_weeks_is_list(self):
        result = build_activity_chart(self.qs, self.start)
        self.assertIsInstance(result['weeks'], list)

    def test_each_week_is_list(self):
        result = build_activity_chart(self.qs, self.start)
        for week in result['weeks']:
            self.assertIsInstance(week, list)

    def test_real_days_have_required_keys(self):
        result = build_activity_chart(self.qs, self.start)
        for day in _all_real_days(result):
            self.assertIn('date', day)
            self.assertIn('count', day)
            self.assertIn('level', day)
            self.assertIn('title', day)

    def test_365_days_of_data(self):
        result = build_activity_chart(self.qs, self.start)
        real_days = _all_real_days(result)
        # build_activity_chart covers start_date through start_date + 365 (366 days inclusive)
        self.assertEqual(len(real_days), 366)

    def test_empty_queryset_all_zero_counts(self):
        result = build_activity_chart(self.qs, self.start)
        for day in _all_real_days(result):
            self.assertEqual(day['count'], 0)

    def test_level_0_for_zero_bookmarks(self):
        result = build_activity_chart(self.qs, self.start)
        for day in _all_real_days(result):
            self.assertEqual(day['level'], 0)

    def _create_bookmarks_on_date(self, count, target_date):
        dt = timezone.make_aware(
            timezone.datetime(target_date.year, target_date.month, target_date.day, 12, 0, 0)
        )
        for i in range(count):
            Bookmark.objects.create(url=f'https://example.com/{i}', date_added=dt)

    def _get_day_for_date(self, result, target_date):
        target_str = str(target_date)
        for week in result['weeks']:
            for day in week:
                if day.get('date') == target_str:
                    return day
        return None

    def test_level_1_for_one_bookmark(self):
        target = self.start + timedelta(days=10)
        self._create_bookmarks_on_date(1, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertIsNotNone(day)
        self.assertEqual(day['level'], 1)

    def test_level_1_for_two_bookmarks(self):
        target = self.start + timedelta(days=10)
        self._create_bookmarks_on_date(2, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertEqual(day['level'], 1)

    def test_level_2_for_three_bookmarks(self):
        target = self.start + timedelta(days=10)
        self._create_bookmarks_on_date(3, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertEqual(day['level'], 2)

    def test_level_2_for_four_bookmarks(self):
        target = self.start + timedelta(days=10)
        self._create_bookmarks_on_date(4, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertEqual(day['level'], 2)

    def test_level_3_for_five_bookmarks(self):
        target = self.start + timedelta(days=10)
        self._create_bookmarks_on_date(5, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertEqual(day['level'], 3)

    def test_level_3_for_seven_bookmarks(self):
        target = self.start + timedelta(days=10)
        self._create_bookmarks_on_date(7, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertEqual(day['level'], 3)

    def test_level_4_for_eight_bookmarks(self):
        target = self.start + timedelta(days=10)
        self._create_bookmarks_on_date(8, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertEqual(day['level'], 4)

    def test_bookmark_appears_on_correct_date(self):
        target = date(2024, 3, 15)
        self._create_bookmarks_on_date(2, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertIsNotNone(day)
        self.assertEqual(day['count'], 2)

    def test_title_format_singular(self):
        target = self.start + timedelta(days=5)
        self._create_bookmarks_on_date(1, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertIn('1 bookmark', day['title'])
        self.assertNotIn('bookmarks', day['title'])

    def test_title_format_plural(self):
        target = self.start + timedelta(days=5)
        self._create_bookmarks_on_date(2, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertIn('2 bookmarks', day['title'])

    def test_clickable_true_when_count_positive(self):
        target = self.start + timedelta(days=5)
        self._create_bookmarks_on_date(1, target)
        result = build_activity_chart(self.qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertTrue(day.get('clickable'))

    def test_clickable_false_when_count_zero(self):
        result = build_activity_chart(self.qs, self.start)
        for day in _all_real_days(result):
            self.assertFalse(day.get('clickable', False))

    def test_month_labels_is_list_of_dicts(self):
        result = build_activity_chart(self.qs, self.start)
        self.assertIsInstance(result['month_labels'], list)
        for label in result['month_labels']:
            self.assertIsInstance(label, dict)
            self.assertIn('week_index', label)
            self.assertIn('offset', label)
            self.assertIn('label', label)

    def test_month_labels_are_valid_abbreviations(self):
        result = build_activity_chart(self.qs, self.start)
        valid_abbrs = list(calendar.month_abbr[1:])
        for label in result['month_labels']:
            self.assertIn(label['label'], valid_abbrs)

    def test_month_labels_generated_for_year(self):
        result = build_activity_chart(self.qs, self.start)
        # A full year starting Jan 1 should produce at least 12 month labels
        self.assertGreaterEqual(len(result['month_labels']), 12)

    def test_queryset_filter_respected(self):
        target = self.start + timedelta(days=10)
        dt = timezone.make_aware(
            timezone.datetime(target.year, target.month, target.day, 12, 0, 0)
        )
        Bookmark.objects.create(url='https://public.com', private=False, date_added=dt)
        Bookmark.objects.create(url='https://private.com', private=True, date_added=dt)

        public_qs = Bookmark.objects.filter(private=False)
        result = build_activity_chart(public_qs, self.start)
        day = self._get_day_for_date(result, target)
        self.assertEqual(day['count'], 1)
