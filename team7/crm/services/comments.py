from typing import Optional, List, Dict, Any

from django.db import transaction
from django.utils import timezone

from crm.models import CmrComment
from .errors import BadRequest, NotFound, Forbidden
from .identity import ensure_user, ensure_target

ALLOWED_COMMENT_STATUSES = {"pending", "approved", "rejected", "all"}


def _validate_status(status: str, allowed: set[str]) -> None:
    if status not in allowed:
        raise BadRequest(f"Invalid status '{status}'. Allowed: {sorted(allowed)}")


@transaction.atomic
def post_comment(
    user_id: str,
    target_id: str,
    body: str,
    parent_comment_id: Optional[str] = None,
    username: Optional[str] = None,
) -> CmrComment:
    if not user_id:
        raise BadRequest("user_id is required")
    if not target_id:
        raise BadRequest("target_id is required")
    if body is None:
        raise BadRequest("body is required")

    body = body.strip()
    if not (1 <= len(body) <= 2000):
        raise BadRequest("body must be 1..2000 characters")

    user = ensure_user(user_id, username=username)
    target = ensure_target(target_id)
    now = timezone.now()

    # -------------------------
    # Replies: do NOT replace
    # -------------------------
    if parent_comment_id:
        try:
            parent = CmrComment.objects.select_for_update().get(
                id_comment=parent_comment_id,
                deleted_at__isnull=True,
            )
        except CmrComment.DoesNotExist:
            raise NotFound("parent comment not found")

        # only one level reply
        if parent.parent_comment_id is not None:
            raise BadRequest("reply-to-reply is not allowed (max depth = 2)")
        if parent.id_target_id != target.id_target:
            raise BadRequest("parent comment must belong to same target")

        return CmrComment.objects.create(
            id_target=target,
            user=user,
            parent_comment=parent,
            body=body,
            status="approved",  # visible immediately
            report_count=0,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

    # ---------------------------------------------------
    # Top-level: replace previous comment by same user+target
    # ---------------------------------------------------
    existing = (
        CmrComment.objects.select_for_update()
        .filter(
            deleted_at__isnull=True,
            id_target_id=target.id_target,
            user_id=user.id_user,
            parent_comment_id__isnull=True,
        )
        .order_by("-created_at")
    )

    first = existing.first()
    if first:
        # update latest one in place (true "replace")
        first.body = body
        first.status = "approved"
        first.updated_at = now
        first.save(update_fields=["body", "status", "updated_at"])

        # soft-delete any older duplicates
        (existing.exclude(id_comment=first.id_comment)).update(deleted_at=now)
        return first

    # no previous comment -> create new top-level
    return CmrComment.objects.create(
        id_target=target,
        user=user,
        parent_comment=None,
        body=body,
        status="approved",
        report_count=0,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )


def get_comments(
    target_id: Optional[str],
    status: str,
    parent_comment_id: Optional[str],
) -> List[Dict[str, Any]]:
    _validate_status(status, ALLOWED_COMMENT_STATUSES)

    # Always hide soft-deleted comments
    qs = CmrComment.objects.filter(deleted_at__isnull=True)

    # 🔥 FIX: "all" should NOT include rejected
    if status == "all":
        qs = qs.filter(status__in=["approved", "pending"])
    else:
        qs = qs.filter(status=status)

    if target_id:
        qs = qs.filter(id_target_id=target_id)

    if parent_comment_id:
        qs = qs.filter(parent_comment_id=parent_comment_id)
    else:
        qs = qs.filter(parent_comment_id__isnull=True)

    qs = qs.select_related("user").order_by("-created_at")

    out: List[Dict[str, Any]] = []
    for c in qs:
        out.append(
            {
                "id_comment": c.id_comment,
                "user_id": c.user_id,  # REQUIRED for UI canEdit()
                "user_name": c.user.username,
                "body": c.body,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "report_count": c.report_count,
                "status": c.status,
                "parent_comment_id": c.parent_comment_id,
                "target_id": c.id_target_id,
            }
        )

    return out



@transaction.atomic
def edit_comment(
    user_id: str,
    comment_id: str,
    body: str,
    username: Optional[str] = None,
) -> CmrComment:
    if not user_id:
        raise BadRequest("user_id is required")
    if not comment_id:
        raise BadRequest("comment_id is required")
    if body is None:
        raise BadRequest("body is required")

    body = body.strip()
    if not (1 <= len(body) <= 2000):
        raise BadRequest("body must be 1..2000 characters")

    # IMPORTANT: normalize user_id by using ensure_user (so types match)
    user = ensure_user(user_id, username=username)

    try:
        comment = CmrComment.objects.select_for_update().get(
            id_comment=comment_id,
            deleted_at__isnull=True
        )
    except CmrComment.DoesNotExist:
        raise NotFound("comment not found")

    # Only the owner can edit
    if str(comment.user_id) != str(user.id_user):
        raise Forbidden("you can only edit your own comment")

    comment.body = body
    comment.updated_at = timezone.now()
    comment.save(update_fields=["body", "updated_at"])
    return comment


@transaction.atomic
def update_comment_status(
    moderator_user_id: str,
    comment_id: str,
    status: str,
    moderator_username: Optional[str] = None,
) -> CmrComment:
    _validate_status(status, {"pending", "approved", "rejected"})

    moderator = ensure_user(moderator_user_id, username=moderator_username)
    if not moderator.is_moderator:
        raise Forbidden("moderator privileges required")

    try:
        comment = CmrComment.objects.select_for_update().get(
            id_comment=comment_id,
            deleted_at__isnull=True,
        )
    except CmrComment.DoesNotExist:
        raise NotFound("comment not found")

    comment.status = status
    comment.save(update_fields=["status"])
    return comment
