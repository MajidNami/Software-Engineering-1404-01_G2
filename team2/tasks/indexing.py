from elasticsearch import Elasticsearch
from django.conf import settings
from team2.models import Version

ES = Elasticsearch(
    hosts=[settings.ELASTICSEARCH_URL]
)
INDEX_NAME = "articles"

def index_article_version(version: Version):
    # Index a version of an article in Elasticsearch

    body = {
        "article_name": version.article.name,
        "version_name": version.name,
        "content": version.content,
        "summary": version.summary,
        "tags": [tag.name for tag in version.tags.all()],
    }

    ES.index(index=INDEX_NAME, id=version.name, document=body)


def search_articles_semantic(query, size=10):
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["content^2", "summary", "tags"],
                "fuzziness": "AUTO"
            }
        },
        "size": size
    }

    resp = ES.search(index=INDEX_NAME, body=search_body)
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
