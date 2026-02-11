from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.auth import api_login_required
from .authentication import JWTMiddlewareAuthentication
from .models import Article, Version, Vote
from .serializers import (
    ArticleSerializer, VersionSerializer, CreateArticleSerializer,
    CreateVersionFromVersionSerializer, VoteSerializer,
)
from .tasks.tasks import summarize_article, tag_article
from .tasks.indexing import index_article_version, search_articles_semantic

TEAM_NAME = "team2"

AUTH_CLASSES = [JWTMiddlewareAuthentication]
PERM_CLASSES = [IsAuthenticated]


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")


@api_view(['POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def create_article(request):
    serializer = CreateArticleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    name = serializer.validated_data['name']

    if Article.objects.filter(name=name).exists():
        return Response(
            {"detail": "Article with this name already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    article = Article.objects.create(
        name=name,
        creator_id=request.user.id,
        score=0,
    )

    default_version = Version.objects.create(
        name=f"{name}-v1",
        article=article,
        content='',
        summary='',
        editor_id=request.user.id,
    )

    article.current_version = default_version
    article.save()

    return Response(ArticleSerializer(article).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def get_article(request, article_name):
    article = get_object_or_404(Article, name=article_name)
    return Response(ArticleSerializer(article).data)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def get_version(request, version_name):
    version = get_object_or_404(Version, name=version_name)
    return Response(VersionSerializer(version).data)


@api_view(['POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def create_version_from_version(request):
    serializer = CreateVersionFromVersionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    source_name = serializer.validated_data['source_version_name']
    new_name = serializer.validated_data['new_version_name']

    source_version = get_object_or_404(Version, name=source_name)

    if Version.objects.filter(name=new_name).exists():
        return Response(
            {"detail": "Version with this name already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    new_version = Version.objects.create(
        name=new_name,
        article=source_version.article,
        content=source_version.content,
        summary=source_version.summary,
        editor_id=request.user.id,
    )
    new_version.tags.set(source_version.tags.all())

    article = source_version.article
    article.current_version = new_version
    article.save()

    return Response(VersionSerializer(new_version).data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def vote(request):
    serializer = VoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    article_name = serializer.validated_data['article_name']
    value = serializer.validated_data['value']

    article = get_object_or_404(Article, name=article_name)
    user_id = request.user.id

    with transaction.atomic():
        existing_vote = Vote.objects.filter(user_id=user_id, article=article).first()

        if existing_vote:
            if existing_vote.value == value:
                return Response(
                    {"detail": "You have already voted this way."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            old_value = existing_vote.value
            existing_vote.value = value
            existing_vote.save()
            article.score += value - old_value
        else:
            Vote.objects.create(user_id=user_id, article=article, value=value)
            article.score += value

        article.save()

    return Response({"article": article.name, "score": article.score, "your_vote": value})


@api_view(['POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def publish_version(request, version_name):
    version = get_object_or_404(Version, name=version_name)
    article = version.article

    article.current_version = version
    article.save()

    tag_article(article.name)
    summarize_article(article.name)

    index_article_version(version)

    return Response(ArticleSerializer(article).data)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def search_articles(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return Response({"detail": "Query missing"}, status=400)

    results = search_articles_semantic(query)
    return Response({"query": query, "results": results})
