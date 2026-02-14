import re
import time
import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.db import transaction
from rest_framework import status

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from core.auth import api_login_required
from .authentication import JWTMiddlewareAuthentication
from django.db.models import Prefetch
from .models import Article, Version, Vote, PublishRequest, Tag
from celery import chord
from .serializers import (
    ArticleSerializer, VersionSerializer, CreateArticleSerializer,
    CreateVersionFromVersionSerializer, CreateEmptyVersionSerializer, VoteSerializer,
    PublishRequestSerializer, CreatePublishRequestSerializer,
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
    return redirect(settings.TEAM2_FRONT_URL)


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
@permission_classes([AllowAny])
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


@api_view(['PATCH'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def update_version(request, version_name):
    version = get_object_or_404(Version, name=version_name)
    serializer = VersionSerializer(version, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(VersionSerializer(version).data)


@api_view(['POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def publish_version(request, version_name):
    version = get_object_or_404(Version, name=version_name)
    article = version.article

    if str(article.creator_id) != str(request.user.id):
        return Response(
            {"detail": "Only the article creator can publish directly."},
            status=status.HTTP_403_FORBIDDEN,
        )

    article.current_version = version
    article.save()

    chord(
        [tag_article.s(article.name), summarize_article.s(article.name)]
    )(index_article_version.s(version.name))

    return Response(ArticleSerializer(article).data)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def my_articles(request):
    articles = Article.objects.filter(
        creator_id=request.user.id
    ).select_related('current_version').prefetch_related('versions')
    article_list = list(articles)

    data = ArticleSerializer(article_list, many=True).data

    resp = Response(data)
    return resp


@api_view(['POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def create_empty_version(request):
    serializer = CreateEmptyVersionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    article_name = serializer.validated_data['article_name']
    version_name = serializer.validated_data['version_name']

    article = get_object_or_404(Article, name=article_name)

    if Version.objects.filter(name=version_name).exists():
        return Response(
            {"detail": "Version with this name already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    new_version = Version.objects.create(
        name=version_name,
        article=article,
        content='',
        summary='',
        editor_id=request.user.id,
    )

    return Response(VersionSerializer(new_version).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes([AllowAny])
def search_articles(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return Response({"detail": "Query missing"}, status=400)

    try:
        results = search_articles_semantic(query)
    except Exception as e:
        return Response(
            {"detail": f"Search service unavailable: {e}"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    resp = Response({"query": query, "results": results})
    return resp


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes([AllowAny])
def wiki_content(request):
    content = request.GET.get("content", "").strip()
    if not content:
        return Response({"detail": "Query parameter 'content' is required."}, status=400)

    try:
        results = search_articles_semantic(content, size=1)
    except Exception as e:
        return Response(
            {"detail": f"Search service unavailable: {e}"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if not results:
        return Response({"detail": "No results found."}, status=404)

    hit = results[0]
    article_name = hit["article_name"]

    try:
        article = Article.objects.select_related('current_version').get(name=article_name)
    except Article.DoesNotExist:
        return Response({"detail": "Article not found."}, status=404)

    version = article.current_version
    content = version.content if version else ""
    summary = version.summary if version else ""
    tags = hit.get("tags", [])

    images = re.findall(r'!\[.*?\]\((https?://\S+?)\)', content)

    return Response({
        "tags": tags,
        "summary": summary,
        "description": content,
        "images": images,
        "url": f"/articles/{article_name}",
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
    })


@api_view(['POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def request_publish(request):
    serializer = CreatePublishRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    version_name = serializer.validated_data['version_name']
    version = get_object_or_404(Version, name=version_name)
    article = version.article

    if PublishRequest.objects.filter(
        version=version, requester_id=request.user.id, status='pending'
    ).exists():
        return Response(
            {"detail": "You already have a pending request for this version."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    pub_request = PublishRequest.objects.create(
        version=version,
        article=article,
        requester_id=request.user.id,
    )

    return Response(PublishRequestSerializer(pub_request).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def list_publish_requests(request, article_name):
    article = get_object_or_404(Article, name=article_name)

    if str(article.creator_id) != str(request.user.id):
        return Response(
            {"detail": "Only the article creator can view publish requests."},
            status=status.HTTP_403_FORBIDDEN,
        )

    requests_qs = PublishRequest.objects.filter(
        article=article, status='pending'
    ).select_related('version')

    return Response(PublishRequestSerializer(requests_qs, many=True).data)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def my_publish_requests(request, article_name):
    article = get_object_or_404(Article, name=article_name)

    requests_qs = PublishRequest.objects.filter(
        article=article, requester_id=request.user.id
    ).select_related('version').order_by('-created_at')

    return Response(PublishRequestSerializer(requests_qs, many=True).data)


@api_view(['POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def approve_publish_request(request, pk):
    pub_request = get_object_or_404(PublishRequest, pk=pk)
    article = pub_request.article

    if str(article.creator_id) != str(request.user.id):
        return Response(
            {"detail": "Only the article creator can approve requests."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if pub_request.status != 'pending':
        return Response(
            {"detail": "This request has already been processed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    pub_request.status = 'approved'
    pub_request.save()

    version = pub_request.version
    article.current_version = version
    article.save()

    chord(
        [tag_article.s(article.name), summarize_article.s(article.name)]
    )(index_article_version.s(version.name))

    return Response(PublishRequestSerializer(pub_request).data)


@api_view(['POST'])
@authentication_classes(AUTH_CLASSES)
@permission_classes(PERM_CLASSES)
def reject_publish_request(request, pk):
    pub_request = get_object_or_404(PublishRequest, pk=pk)
    article = pub_request.article

    if str(article.creator_id) != str(request.user.id):
        return Response(
            {"detail": "Only the article creator can reject requests."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if pub_request.status != 'pending':
        return Response(
            {"detail": "This request has already been processed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    pub_request.status = 'rejected'
    pub_request.save()

    return Response(PublishRequestSerializer(pub_request).data)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes([AllowAny])
def newest_articles(request):
    articles = Article.objects.filter(
        current_version__isnull=False
    ).select_related('current_version').order_by('-updated_at')[:10]

    data = []
    for a in articles:
        v = a.current_version
        data.append({
            "name": a.name,
            "summary": v.summary if v else "",
            "score": a.score,
        })
    return Response(data)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes([AllowAny])
def top_rated_articles(request):
    articles = Article.objects.filter(
        current_version__isnull=False
    ).select_related('current_version').order_by('-score')[:10]

    data = []
    for a in articles:
        v = a.current_version
        data.append({
            "name": a.name,
            "summary": v.summary if v else "",
            "score": a.score,
        })
    return Response(data)


@api_view(['GET'])
@authentication_classes(AUTH_CLASSES)
@permission_classes([AllowAny])
def top_articles_by_tag(request):
    tags = Tag.objects.all()
    result = []

    for tag in tags:
        articles = Article.objects.filter(
            current_version__isnull=False,
            current_version__tags=tag,
        ).select_related('current_version').order_by('-score')[:3]

        if not articles:
            continue

        items = []
        for a in articles:
            v = a.current_version
            items.append({
                "name": a.name,
                "summary": v.summary if v else "",
                "score": a.score,
            })

        result.append({
            "tag": tag.name,
            "articles": items,
        })

    return Response(result)
