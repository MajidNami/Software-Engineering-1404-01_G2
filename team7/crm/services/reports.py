from typing import Optional, List, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from crm.models import CmrReport, CmrComment, CmrMedia
from .errors import BadRequest, NotFound, Forbidden
from .identity import ensure_user

ALLOWED_REPORT_STATUSES = {"pending", "valid", "invalid"}


@transaction.atomic
def create_report(
    reporter_user_id: str,
    reason: Optional[str],
    details: Optional[str],
    media_or_comment: int,
    target_id: str,
    username: Optional[str] = None,
) -> CmrReport:
    reporter = ensure_user(reporter_user_id, username=username)
    now = timezone.now()

    is_comment = int(media_or_comment) == 1
    is_media = int(media_or_comment) == 0
    if not (is_comment or is_media):
        raise BadRequest("media_or_comment must be 0 (media) or 1 (comment)")

    comment = None
    media = None

    if is_comment:
        try:
            comment = CmrComment.objects.select_for_update().get(
                id_comment=target_id,
                deleted_at__isnull=True
            )
        except CmrComment.DoesNotExist:
            raise NotFound("comment not found")

        if CmrReport.objects.filter(reporter=reporter, comment=comment).exists():
            raise BadRequest("you already reported this comment")

        comment.report_count = int(comment.report_count) + 1
        if int(comment.report_count) >= settings.REPORT_THRESHOLD and comment.status == "approved":
            comment.status = "pending"
            comment.save(update_fields=["report_count", "status"])
        else:
            comment.save(update_fields=["report_count"])

    if is_media:
        try:
            media = CmrMedia.objects.select_for_update().get(
                id_media=target_id,
                deleted_at__isnull=True
            )
        except CmrMedia.DoesNotExist:
            raise NotFound("media not found")

        if CmrReport.objects.filter(reporter=reporter, media=media).exists():
            raise BadRequest("you already reported this media")

        media.report_count = int(media.report_count) + 1
        if int(media.report_count) >= settings.REPORT_THRESHOLD and media.status == "approved":
            media.status = "pending"
            media.save(update_fields=["report_count", "status"])
        else:
            media.save(update_fields=["report_count"])

    rep = CmrReport.objects.create(
        reporter=reporter,
        reason=reason,
        details=details,
        status="pending",
        comment=comment,
        media=media,
        created_at=now,
    )
    return rep


def get_pending_reports(moderator_user_id: str) -> List[Dict[str, Any]]:
    moderator = ensure_user(moderator_user_id)
    if not moderator.is_moderator:
        raise Forbidden("moderator privileges required")

    qs = (
        CmrReport.objects
        .filter(status="pending")
        .select_related(
            "reporter",
            "comment", "comment__user",
            "media", "media__user",
        )
        .order_by("-created_at")
    )

    out: List[Dict[str, Any]] = []
    for r in qs:
        # who is being reported?
        reported_user_id = None
        reported_username = None

        if r.comment_id and r.comment and r.comment.user:
            reported_user_id = r.comment.user_id
            reported_username = r.comment.user.username
        elif r.media_id and r.media and r.media.user:
            reported_user_id = r.media.user_id
            reported_username = r.media.user.username

        out.append({
            "id_report": r.id_report,
            "reporter_user_id": r.reporter_id,
            "reporter_username": r.reporter.username,

            # ✅ NEW fields for moderator UI
            "reported_user_id": reported_user_id,
            "reported_username": reported_username,

            "reason": r.reason,
            "details": r.details,
            "id_comment": r.comment_id,
            "id_media": r.media_id,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return out


@transaction.atomic
def update_report_status(moderator_user_id: str, report_id: str, status: str) -> CmrReport:
    if status not in ALLOWED_REPORT_STATUSES:
        raise BadRequest("invalid report status")

    moderator = ensure_user(moderator_user_id)
    if not moderator.is_moderator:
        raise Forbidden("moderator privileges required")

    try:
        rep = (
            CmrReport.objects
            .select_for_update()
            .select_related("comment", "media")
            .get(id_report=report_id)
        )
    except CmrReport.DoesNotExist:
        raise NotFound("report not found")

    rep.status = status
    rep.save(update_fields=["status"])

    # ✅ If report is valid => reject + soft-delete the related content
    if status == "valid":
        now = timezone.now()

        if rep.comment_id:
            CmrComment.objects.filter(id_comment=rep.comment_id).update(
                status="rejected",
                deleted_at=now
            )

        if rep.media_id:
            CmrMedia.objects.filter(id_media=rep.media_id).update(
                status="rejected",
                deleted_at=now
            )

    return rep
