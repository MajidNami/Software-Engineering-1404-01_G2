"""
Internal API endpoints called by the AI service (callbacks).
Protected by a shared INTERNAL_API_KEY header.
"""
import logging
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import BasePermission

from .models import Post, Media
from .utils import log_activity, create_notification

logger = logging.getLogger(__name__)

# Thresholds
# score >= REJECT  → REJECTED outright
# score >= REVIEW  → PENDING_ADMIN (needs human review)
# score <  REVIEW  → APPROVED


def _decide_status(score: float) -> str:
    """Map a 0-1 bad-content score to a content_status value."""
    if score >= settings.AI_REJECT_THRESHOLD:
        return "REJECTED"
    if score >= settings.AI_REVIEW_THRESHOLD:
        return "PENDING_ADMIN"
    return "APPROVED"


# Permission

class IsInternalService(BasePermission):
    """Validates X-Internal-Key header matches INTERNAL_API_KEY."""

    def has_permission(self, request, view):
        key = request.META.get("HTTP_X_INTERNAL_KEY", "")
        return key == settings.INTERNAL_API_KEY


# Post-level status reconciliation

def _reconcile_post_status(post: Post):
    """
    After either text or media AI verdict arrives, check if BOTH components
    are done. If so, compute the final post status.

    Rules:
    - If any component is still PENDING_AI → do nothing (wait)
    - If any component is REJECTED → whole post REJECTED
    - If any component is PENDING_ADMIN → whole post PENDING_ADMIN
    - Otherwise → APPROVED
    """
    # Still waiting for a verdict
    if post.text_ai_status == "PENDING_AI":
        return
    if post.media_ai_status == "PENDING_AI":
        return

    statuses = [post.text_ai_status]
    if post.media_ai_status is not None:
        statuses.append(post.media_ai_status)

    if "REJECTED" in statuses:
        post.status = "REJECTED"
    elif "PENDING_ADMIN" in statuses:
        post.status = "PENDING_ADMIN"
    else:
        post.status = "APPROVED"

    post.save(update_fields=["status"])

    # Notify user
    if post.status == "APPROVED":
        create_notification(post.user, "Post approved", "Your post has been approved and is now visible.")
    elif post.status == "REJECTED":
        reason = post.rejection_reason or "Content policy violation"
        create_notification(post.user, "Post rejected", f"Your post was rejected: {reason}")
    elif post.status == "PENDING_ADMIN":
        create_notification(post.user, "Post under review", "Your post is being reviewed by a moderator.")


# Endpoints

@api_view(["PATCH"])
@permission_classes([IsInternalService])
def post_ai_verdict(request, post_id):
    """Called by AI service after text moderation completes. Receives raw score."""
    try:
        post = Post.objects.get(post_id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "post not found"}, status=status.HTTP_404_NOT_FOUND)

    score = request.data.get("score")
    if score is None:
        return Response({"error": "score is required"}, status=status.HTTP_400_BAD_REQUEST)

    score = float(score)
    decided = _decide_status(score)
    post.text_ai_status = decided
    post.ai_confidence = score
    if decided == "REJECTED":
        post.rejection_reason = "AI text moderation: inappropriate content detected"

    post.save(update_fields=["text_ai_status", "ai_confidence", "rejection_reason"])
    log_activity(None, "AI_TEXT_VERDICT", target_id=post_id, metadata={"decided": decided, "score": score})

    _reconcile_post_status(post)

    return Response({"post_id": post_id, "text_ai_status": decided, "final_status": post.status})


@api_view(["PATCH"])
@permission_classes([IsInternalService])
def media_ai_verdict(request, media_id):
    """Called by AI service after image moderation completes. Receives raw score."""
    try:
        media = Media.objects.get(media_id=media_id)
    except Media.DoesNotExist:
        return Response({"error": "media not found"}, status=status.HTTP_404_NOT_FOUND)

    score = request.data.get("score")
    if score is None:
        return Response({"error": "score is required"}, status=status.HTTP_400_BAD_REQUEST)

    score = float(score)
    decided = _decide_status(score)
    media.status = decided
    media.ai_confidence = score
    if decided == "REJECTED":
        media.rejection_reason = "AI image moderation: inappropriate content detected"

    media.save(update_fields=["status", "ai_confidence", "rejection_reason"])
    log_activity(None, "AI_MEDIA_VERDICT", target_id=str(media_id), metadata={"decided": decided, "score": score})

    # Notify media owner
    if decided == "APPROVED":
        create_notification(media.user, "Media approved", "Your uploaded media has been approved.")
    elif decided == "REJECTED":
        create_notification(media.user, "Media rejected", "Your uploaded media was rejected.")
    elif decided == "PENDING_ADMIN":
        create_notification(media.user, "Media under review", "Your media is being reviewed by a moderator.")

    # Also update any posts that reference this media
    posts_with_media = Post.objects.filter(media=media, deleted_at__isnull=True)
    for post in posts_with_media:
        post.media_ai_status = decided
        post.save(update_fields=["media_ai_status"])
        _reconcile_post_status(post)

    return Response({"media_id": str(media_id), "status": decided})


@api_view(["PATCH"])
@permission_classes([IsInternalService])
def media_tag(request, media_id):
    """Called by AI service after image tagging/classification completes."""
    try:
        media = Media.objects.get(media_id=media_id)
    except Media.DoesNotExist:
        return Response({"error": "media not found"}, status=status.HTTP_404_NOT_FOUND)

    detected_place = request.data.get("detected_place")
    confidence = request.data.get("confidence", 0.0)

    log_activity(None, "AI_MEDIA_TAG", target_id=str(media_id), metadata={
        "detected_place": detected_place, "confidence": confidence,
    })

    return Response({"media_id": str(media_id), "detected_place": detected_place})
