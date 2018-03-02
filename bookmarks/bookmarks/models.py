from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.conf import settings

from taggit.managers import TaggableManager

import requests


class Bookmark(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(default=timezone.now, blank=True)
    tags = TaggableManager(blank=True)
    private = models.BooleanField(default=False)
    url = models.URLField(max_length=500)

    def __unicode__(self):
        return "{}: {} [{}]".format(
            self.pk,
            self.title[:40],
            self.date_added
        )


@receiver(models.signals.post_save, sender=Bookmark)
def bookmark_pre_save_handler(sender, instance, created, *args, **kwargs):
    # Only run for new items, not updates
    if created:
        if not hasattr(settings, 'SLACK_WEBHOOK_URL'):
            return

        payload = {
            'channel': "#bookmarks-dev",
            'username': "Bookmarks",
            'text': "<{}|{}>\n{}".format(
                instance.url,
                instance.title,
                instance.description,
            ),
            'icon_emoji': ":blue_book:",
            'unfurl_links': True
        }

        requests.post(settings.SLACK_WEBHOOK_URL, json=payload)
