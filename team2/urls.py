from django.urls import path
from . import views

urlpatterns = [
    path("", views.base),
    path("ping/", views.ping),
    path("api/articles/create/", views.create_article, name="team2-create-article"),
    path("api/articles/mine/", views.my_articles, name="team2-my-articles"),
    path("api/articles/search/", views.search_articles, name="team2-search-articles"),
    path("api/articles/newest/", views.newest_articles, name="team2-newest-articles"),
    path("api/articles/top-rated/", views.top_rated_articles, name="team2-top-rated-articles"),
    path("api/articles/top-by-tag/", views.top_articles_by_tag, name="team2-top-by-tag"),
    path("api/articles/<str:article_name>/", views.get_article, name="team2-get-article"),
    path("api/versions/create/", views.create_version_from_version, name="team2-create-version"),
    path("api/versions/create-empty/", views.create_empty_version, name="team2-create-empty-version"),
    path("api/versions/<str:version_name>/", views.get_version, name="team2-get-version"),
    path("api/versions/<str:version_name>/update/", views.update_version, name="team2-update-version"),
    path("api/versions/<str:version_name>/publish/", views.publish_version, name="team2-publish-version"),
    path("api/vote/", views.vote, name="team2-vote"),
    path("api/publish-requests/create/", views.request_publish, name="team2-request-publish"),
    path("api/publish-requests/article/<str:article_name>/", views.list_publish_requests, name="team2-list-publish-requests"),
    path("api/publish-requests/mine/<str:article_name>/", views.my_publish_requests, name="team2-my-publish-requests"),
    path("api/publish-requests/<int:pk>/approve/", views.approve_publish_request, name="team2-approve-publish-request"),
    path("api/publish-requests/<int:pk>/reject/", views.reject_publish_request, name="team2-reject-publish-request"),
    path("api/wiki/", views.wiki_content, name="team2-wiki-content"),
]