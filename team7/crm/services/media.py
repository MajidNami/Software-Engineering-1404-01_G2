from typing import Optional, List, Dict, Any
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage

from crm.models import CmrMedia
from .errors import BadRequest, NotFound, Forbidden
from .identity import ensure_user, ensure_target

ALLOWED_MEDIA_STATUSES = {"pending", "approved", "rejected", "all"}
ALLOWED_MEDIA_TYPES = {"image", "video"}


def list_media(target_id: Optional[str] = None, status: str = "approved") -> List[Dict[str, Any]]:
    if status not in ALLOWED_MEDIA_STATUSES:
        raise BadRequest("invalid status")

    qs = CmrMedia.objects.filter(deleted_at__isnull=True).select_related("user")

    if status != "all":
        qs = qs.filter(status=status)

    if target_id:
        qs = qs.filter(id_target_id=target_id)

    qs = qs.order_by("-created_at")

    out: List[Dict[str, Any]] = []
    for m in qs:
        out.append({
            "id_media": m.id_media,
            "target_id": m.id_target_id,
            "user_id": m.user_id,
            "user_name": m.user.username if m.user else None,
            "media_type": m.media_type,
            "public_url": m.public_url,
            "mime_type": m.mime_type,
            "size_bytes": m.size_bytes,
            "status": m.status,
            "report_count": m.report_count,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })
    return out


@transaction.atomic
def upload_media(
    user_id: str,
    target_id: str,
    file_obj,
    media_type: Optional[str] = None,
    username: Optional[str] = None
) -> CmrMedia:
    if file_obj is None:
        raise BadRequest("file is required")

    user = ensure_user(user_id, username=username)
    target = ensure_target(target_id)

    ct = getattr(file_obj, "content_type", "") or ""
    if not media_type:
        if ct.startswith("image/"):
            media_type = "image"
        elif ct.startswith("video/"):
            media_type = "video"
        else:
            media_type = "image"

    if media_type not in ALLOWED_MEDIA_TYPES:
        raise BadRequest("media_type must be image|video")

    now = timezone.now()
    filename = f"cmr/{target_id}/{now.strftime('%Y%m%d')}/{file_obj.name}"
    saved_path = default_storage.save(filename, file_obj)

    public_url = settings.MEDIA_URL.rstrip("/") + "/" + saved_path

    media = CmrMedia.objects.create(
        id_target=target,
        user=user,
        media_type=media_type,
        object_key=saved_path,
        public_url=public_url,
        mime_type=ct[:100] if ct else None,
        size_bytes=getattr(file_obj, "size", None),
        status="pending",
        report_count=0,
        created_at=now,
        deleted_at=None,
    )
    return media


@transaction.atomic
def update_media_status(moderator_user_id: str, media_id: str, status: str) -> CmrMedia:
    if status not in {"pending", "approved", "rejected"}:
        raise BadRequest("invalid status")

    moderator = ensure_user(moderator_user_id)
    if not moderator.is_moderator:
        raise Forbidden("moderator privileges required")

    try:
        media = CmrMedia.objects.select_for_update().get(id_media=media_id, deleted_at__isnull=True)
    except CmrMedia.DoesNotExist:
        raise NotFound("media not found")

    media.status = status
    if status == "rejected":
        media.deleted_at = timezone.now()
        media.save(update_fields=["status", "deleted_at"])
        return media

    media.save(update_fields=["status"])
    return media


@transaction.atomic
def delete_media(user_id: str, media_id: str) -> CmrMedia:
    if not user_id:
        raise BadRequest("user_id is required")

    try:
        media = CmrMedia.objects.select_for_update().get(id_media=media_id, deleted_at__isnull=True)
    except CmrMedia.DoesNotExist:
        raise NotFound("media not found")

    # only owner can delete (or moderator)
    user = ensure_user(user_id)
    if (media.user_id != user_id) and (not user.is_moderator):
        raise Forbidden("you can only delete your own media")

    media.status = "rejected"
    media.deleted_at = timezone.now()
    media.save(update_fields=["status", "deleted_at"])
    return media
