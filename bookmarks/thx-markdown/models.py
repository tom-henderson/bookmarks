from django.db import models


class MarkdownField(models.TextField):
    
    def __init__(self, *args, **kwargs):
        super(MarkdownField, self).__init__(*args, **kwargs)
