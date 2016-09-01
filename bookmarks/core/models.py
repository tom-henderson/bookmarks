from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from taggit.managers import TaggableManager


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
