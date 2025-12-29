from rest_framework import serializers
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from taggit.serializers import TagListSerializerField, TaggitSerializer
from django.db.models import Count
from bookmarks.models import Bookmark
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
    num_items = serializers.IntegerField()

    class Meta:
        model = Tag
        fields = [
            'name',
            'slug',
            'num_items',
        ]


class API_Bookmarks(ListAPIView):
    queryset = Bookmark.objects.filter(private=False)
    serializer_class = BookmarkSerializer


class API_RecentBookmarks(ListAPIView):
    queryset = Bookmark.objects.filter(private=False).order_by('-date_added')[:10]
    serializer_class = BookmarkSerializer
    
    def get(self, *args, **kwargs):
        response = super().get(*args, **kwargs)
        response['Access-Control-Allow-Origin'] = "*"
        return response


class API_Tags(ListAPIView):
    queryset = Tag.objects.all().order_by('name').annotate(
        num_items=Count('taggit_taggeditem_items')
    )
    serializer_class = TagSerializer


class API_Create(CreateAPIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]
