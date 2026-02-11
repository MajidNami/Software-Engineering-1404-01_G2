from rest_framework import serializers
from .models import Article, Version, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class VersionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Version
        fields = ['name', 'article', 'content', 'summary', 'editor_id', 'tags']
        read_only_fields = ['editor_id']


class ArticleSerializer(serializers.ModelSerializer):
    current_version = VersionSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['name', 'creator_id', 'current_version', 'score']
        read_only_fields = ['creator_id', 'score']


class CreateArticleSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)


class CreateVersionFromVersionSerializer(serializers.Serializer):
    source_version_name = serializers.CharField(max_length=255)
    new_version_name = serializers.CharField(max_length=255)


class VoteSerializer(serializers.Serializer):
    article_name = serializers.CharField(max_length=255)
    value = serializers.ChoiceField(choices=[1, -1])
