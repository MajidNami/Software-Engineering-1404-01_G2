from typing import Optional
from django.db import transaction
from django.utils import timezone
from crm.models import CmrUser, CmrTarget
from crm.models._utils import new_uuid_str
from .errors import BadRequest

@transaction.atomic
def ensure_user(user_id: str, username: Optional[str] = None) -> CmrUser:
    if not user_id:
        raise BadRequest("user_id is required")
    obj, created = CmrUser.objects.get_or_create(
        id_user=user_id,
        defaults={"username": username or f"user-{user_id[:8]}", "email": None, "is_moderator": False},
    )
    if (not created) and username and obj.username != username:
        obj.username = username
        obj.save(update_fields=["username"])
    return obj

@transaction.atomic
def ensure_target(target_id: str, target_name: Optional[str] = None) -> CmrTarget:
    if not target_id:
        raise BadRequest("target_id is required")
    obj, created = CmrTarget.objects.get_or_create(
        id_target=target_id,
        defaults={"entity_type": "tourism_place", "entity_id": new_uuid_str(), "target_name": target_name, "created_at": timezone.now()},
    )
    if (not created) and target_name and obj.target_name != target_name:
        obj.target_name = target_name
        obj.save(update_fields=["target_name"])
    return obj
