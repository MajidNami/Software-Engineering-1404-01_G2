import logging

from celery import shared_task
from django.conf import settings
from team2.models import Article, Version

logger = logging.getLogger(__name__)

INDEX_NAME = "articles"
_ES = None


def _get_es():
    global _ES
    if _ES is None:
        from elasticsearch import Elasticsearch
        _ES = Elasticsearch(hosts=[settings.ELASTICSEARCH_URL])
    return _ES


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def index_article_version(self, results, version_name):
    version = Version.objects.get(name=version_name)
    body = {
        "article_name": version.article.name,
        "version_name": version.name,
        "content": version.content,
        "summary": version.summary,
        "tags": [tag.name for tag in version.tags.all()],
    }

    try:
        _get_es().index(index=INDEX_NAME, id=version.article.name, document=body)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=1, default_retry_delay=30)
def index_all_articles(self):
    es = _get_es()
    articles = Article.objects.filter(
        current_version__isnull=False
    ).select_related('current_version')

    indexed = 0
    for article in articles:
        version = article.current_version
        body = {
            "article_name": article.name,
            "version_name": version.name,
            "content": version.content,
            "summary": version.summary,
            "tags": [tag.name for tag in version.tags.all()],
        }
        try:
            es.index(index=INDEX_NAME, id=article.name, document=body)
            indexed += 1
        except Exception:
            logger.exception("Failed to index article %s", article.name)

    logger.info("Startup indexing complete: %d articles indexed.", indexed)
    return indexed


def search_articles_semantic(query, size=10):
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["content", "summary^2", "tags^3"],
                "fuzziness": "AUTO"
            }
        },
        "size": size
    }

    resp = _get_es().search(index=INDEX_NAME, body=search_body)
    results = []

    for hit in resp["hits"]["hits"]:
        results.append({
            "article_name": hit["_source"]["article_name"],
            "version_name": hit["_source"]["version_name"],
            "score": hit["_score"],
            "summary": hit["_source"]["summary"],
            "tags": hit["_source"]["tags"],
        })

    return results
