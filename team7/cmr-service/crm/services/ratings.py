from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any
from django.db import transaction
from django.utils import timezone

from crm.models import CmrRating, CmrRatingAggregate
from .errors import BadRequest, NotFound
from .identity import ensure_user, ensure_target

def _q2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

@transaction.atomic
def post_rate(user_id: str, target_id: str, rating_value: int, username: Optional[str] = None) -> Dict[str, Any]:
    # postRate must update aggregates and update existing rating if present fileciteturn1file9L4-L7
    if not (1 <= int(rating_value) <= 5):
        raise BadRequest("rating_value must be between 1 and 5")

    user = ensure_user(user_id, username=username)
    target = ensure_target(target_id)

    now = timezone.now()

    # lock aggregates row (or create) to make updates consistent
    aggr, _ = CmrRatingAggregate.objects.select_for_update().get_or_create(
        id_target=target,
        defaults={"rating_count": 0, "rating_sum": 0, "rating_avg": Decimal("0.00"), "updated_at": now},
    )

    # find existing rating (schema doesn't have unique constraint; enforce in app)
    existing = (CmrRating.objects
        .select_for_update()
        .filter(id_target=target, user=user, deleted_at__isnull=True)
        .order_by("-updated_at")
        .first()
    )

    if existing:
        old = int(existing.rating_value)
        new = int(rating_value)
        if old != new:
            existing.rating_value = new
            existing.updated_at = now
            existing.save(update_fields=["rating_value", "updated_at"])
            aggr.rating_sum = int(aggr.rating_sum) - old + new
    else:
        CmrRating.objects.create(
            id_target=target,
            user=user,
            rating_value=int(rating_value),
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )
        aggr.rating_count = int(aggr.rating_count) + 1
        aggr.rating_sum = int(aggr.rating_sum) + int(rating_value)

    count = int(aggr.rating_count)
    s = int(aggr.rating_sum)
    avg = Decimal("0.00") if count == 0 else _q2(Decimal(s) / Decimal(count))
    aggr.rating_avg = avg
    aggr.updated_at = now
    aggr.save(update_fields=["rating_count", "rating_sum", "rating_avg", "updated_at"])

    return {"rating_count": count, "rating_sum": s, "rating_avg": str(avg)}

def get_avg_rate(target_id: str) -> Dict[str, Any]:
    target = ensure_target(target_id)
    aggr = CmrRatingAggregate.objects.filter(id_target=target).first()
    if not aggr:
        return {"rating_count": 0, "rating_sum": 0, "rating_avg": "0.00"}
    return {
        "rating_count": int(aggr.rating_count),
        "rating_sum": int(aggr.rating_sum),
        "rating_avg": str(aggr.rating_avg),
    }

def get_my_rate(target_id: str, user_id: str) -> Optional[int]:
    user = ensure_user(user_id)
    target = ensure_target(target_id)
    rating = (CmrRating.objects
        .filter(id_target=target, user=user, deleted_at__isnull=True)
        .order_by("-updated_at")
        .first()
    )
    return int(rating.rating_value) if rating else None
