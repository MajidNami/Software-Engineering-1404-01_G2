from django.urls import path
from . import views

urlpatterns = [
    path("", views.base),
    path("ping/", views.ping),
    path("api/articles/create/", views.create_article, name="team2-create-article"),
    path("api/articles/<str:article_name>/", views.get_article, name="team2-get-article"),
    path("api/versions/create/", views.create_version_from_version, name="team2-create-version"),
    path("api/versions/<str:version_name>/", views.get_version, name="team2-get-version"),
    path("api/vote/", views.vote, name="team2-vote"),
    path("api/versions/<str:version_name>/publish/", views.publish_version, name="team2-publish-version"),
    path("api/articles/search/", views.search_articles, name="team2-search-articles"),
]