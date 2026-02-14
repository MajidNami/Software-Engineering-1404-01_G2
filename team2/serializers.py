from rest_framework import serializers
from .models import Article, Version, Tag, PublishRequest


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class VersionSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Version
        fields = ['name', 'article', 'content', 'summary', 'editor_id', 'tags', 'created_at', 'updated_at']
        read_only_fields = ['editor_id', 'summary', 'tags', 'created_at', 'updated_at']


class VersionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = ['name', 'summary', 'editor_id', 'created_at', 'updated_at']


class ArticleSerializer(serializers.ModelSerializer):
    current_version = VersionSerializer(read_only=True)
    versions = VersionListSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['name', 'creator_id', 'current_version', 'score', 'versions', 'created_at', 'updated_at']
        read_only_fields = ['creator_id', 'score', 'created_at', 'updated_at']


class CreateArticleSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)


class CreateVersionFromVersionSerializer(serializers.Serializer):
    source_version_name = serializers.CharField(max_length=255)
    new_version_name = serializers.CharField(max_length=255)


class CreateEmptyVersionSerializer(serializers.Serializer):
    article_name = serializers.CharField(max_length=255)
    version_name = serializers.CharField(max_length=255)


class VoteSerializer(serializers.Serializer):
    article_name = serializers.CharField(max_length=255)
    value = serializers.ChoiceField(choices=[1, -1])


class PublishRequestSerializer(serializers.ModelSerializer):
    version_name = serializers.CharField(source='version.name', read_only=True)
    version_summary = serializers.CharField(source='version.summary', read_only=True)
    article_name = serializers.CharField(source='article.name', read_only=True)

    class Meta:
        model = PublishRequest
        fields = ['id', 'version_name', 'version_summary', 'article_name', 'requester_id', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'requester_id', 'status', 'created_at', 'updated_at']


class CreatePublishRequestSerializer(serializers.Serializer):
    version_name = serializers.CharField(max_length=255)
