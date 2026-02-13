import copy
import json
import logging
import re
import sys

from celery import shared_task
from django.conf import settings
from team2.models import Article, Tag, Version
from team2.models import Article, Version

MODEL_NAME = "gemini-2.5-flash"
_CLIENT = None


def _get_client():
    global _CLIENT
    if _CLIENT is None:
        from google import genai
        _CLIENT = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _CLIENT


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def tag_article(self, article_name):
    article = Article.objects.get(name=article_name)
    version_name = article.current_version
    if version_name is None:
        return None

    version = Version.objects.get(name=version_name)
    content = version.content

    existing_tags = list(Tag.objects.values_list("name", flat=True))

    prompt = f"""You are a content classification assistant. Your ONLY output must be a single valid JSON object with no extra text, no markdown fences, no explanation.

Select relevant tags from EXISTING TAGS. Only suggest NEW tags if absolutely necessary. Maximum 5 total tags. Use concise Farsi tags. Prefer existing tags.

Output format (respond with ONLY this JSON, nothing else):
{{"selected_existing_tags": ["tag1"], "new_tags": ["new_tag1"]}}

EXISTING TAGS: {existing_tags}

ARTICLE:
{content}"""

    try:
        response = _get_client().models.generate_content(model=MODEL_NAME, contents=prompt)
        
        text = response.text.strip()
        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'```\s*$', '', text)
        match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if match:
            text = match.group(0)
        data = json.loads(text)

        selected_existing = data.get("selected_existing_tags", [])
        new_tags = data.get("new_tags", [])
    except Exception as exc:
        raise self.retry(exc=exc)

    for tag_name in selected_existing:
        try:
            tag = Tag.objects.get(name=tag_name)
            version.tags.add(tag)
        except Tag.DoesNotExist:
            continue

    for tag_name in new_tags:
        tag, _ = Tag.objects.get_or_create(name=tag_name.lower())
        version.tags.add(tag)

    return {
        "selected_existing_tags": selected_existing,
        "new_tags": new_tags,
    }


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def summarize_article(self, article_name):
    article = Article.objects.get(name=article_name)
    version_name = article.current_version

    if version_name is None:
        return

    version = Version.objects.get(name=version_name)
    content = version.content

    prompt = f"""
You are an assistant that writes concise, neutral summaries.

Summarize the following article in 3–6 sentences in FARSI.
Do not add information that is not present.
Be factual and clear.

ARTICLE:
\"\"\"
{content}
\"\"\"
"""

    try:
        response = _get_client().models.generate_content(model=MODEL_NAME, contents=prompt)
    except Exception as exc:
        raise self.retry(exc=exc)

    summary = response.text.strip()

    version.summary = summary
    version.save(update_fields=["summary"])

    return summary
