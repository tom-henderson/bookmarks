# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-27 07:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20160827_1929'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookmark',
            name='date_added',
        ),
    ]
