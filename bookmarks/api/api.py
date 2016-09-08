from rest_framework import serializers
from rest_framework.generics import ListAPIView
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

from core.models import Bookmark
from taggit.models import Tag


class BookmarkSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Bookmark
        fields = (
            'title',
            'description',
            'date_added',
            'tags',
            'private',
            'url',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'name',
            'slug'
        ]

class API_Bookmarks(ListAPIView):
    queryset = Bookmark.objects.filter(private=False)
    serializer_class = BookmarkSerializer


class API_RecentBookmarks(ListAPIView):
    queryset = Bookmark.objects.filter(private=False).order_by('-date_added')[:10]
    serializer_class = BookmarkSerializer


class API_Tags(ListAPIView):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
