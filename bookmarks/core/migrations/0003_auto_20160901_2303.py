# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-01 11:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_bookmark_tag_import'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookmark',
            name='date_added',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
