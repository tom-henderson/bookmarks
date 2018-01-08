from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from core.models import Bookmark

import json


class Command(BaseCommand):
    def log_message(self, message):
        self.stdout.write(
            u"[{}] {}".format(
                datetime.now(),
                message,
            )
        )

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, **options):
        with open(options['path'], 'r') as file:
            data = json.load(file)

        self.log_message(
            u"Found {} bookmarks".format(len(data))
        )

        for bookmark in data:
            self.log_message(u"{}".format(bookmark['title']))
            b = Bookmark(
                title=bookmark['title'],
                description=bookmark['description'],
                date_added=bookmark['date_added'],
                private=bookmark['private'],
                url=bookmark['url']
            )
            b.save()
            for tag in bookmark['tags']:
                b.tags.add(tag)
