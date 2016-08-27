from __future__ import unicode_literals

from django.db import models

from taggit.managers import TaggableManager


class Bookmark(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    add_date = models.CharField(max_length=200)
    tags = TaggableManager()
    tag_import = models.TextField(blank=True, null=True)
    private = models.BooleanField(default=False)
    url = models.URLField()
