"""
Outbound calls to the AI service (fire-and-forget via thread).
"""
import logging
import threading
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

AI_URL = None  # lazy — read from settings on first call


def _ai_url():
    global AI_URL
    if AI_URL is None:
        AI_URL = settings.AI_SERVICE_URL.rstrip("/")
    return AI_URL


def _fire(fn, *args):
    """Run fn(*args) in a daemon thread — never blocks the request."""
    t = threading.Thread(target=fn, args=args, daemon=True)
    t.start()


def _post(path: str, payload: dict):
    try:
        r = requests.post(f"{_ai_url()}{path}", json=payload, timeout=5)
        r.raise_for_status()
        logger.info("AI request %s → %s", path, r.status_code)
    except Exception:
        logger.exception("AI request failed: %s", path)


# Public API

def submit_text_moderation(post_id: int, content: str):
    """Ask AI service to moderate post text. Non-blocking."""
    _fire(_post, "/api/moderate-text/", {"post_id": post_id, "content": content})


def submit_image_moderation(media_id: str, s3_object_key: str):
    """Ask AI service to moderate an image. Non-blocking."""
    _fire(_post, "/api/moderate-image/", {"media_id": media_id, "s3_object_key": s3_object_key})


def submit_image_tagging(media_id: str, s3_object_key: str):
    """Ask AI service to tag/classify an image. Non-blocking."""
    _fire(_post, "/api/tag-image/", {"media_id": media_id, "s3_object_key": s3_object_key})


def submit_place_summary(place_id: int, comments: list[str], ratings: list[float]):
    """Ask AI service to generate a place summary. Non-blocking."""
    _fire(_post, "/api/summarize-place/", {
        "place_id": place_id, "comments": comments, "ratings": ratings,
    })
