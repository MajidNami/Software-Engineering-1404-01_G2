from django.shortcuts import render
from django.http import HttpRequest
from django.views.decorators.http import require_GET

from crm.services.identity import ensure_user, ensure_target
from crm.services.targets import get_target_name


@require_GET
def target_interaction(request: HttpRequest, target_id: str, user_id: str):
    # Get username from DB (ensure_user returns the DB user row)
    username_hint = request.GET.get("username") or getattr(request.identity, "username", None)
    user = ensure_user(user_id, username=username_hint)

    ensure_target(target_id)

    return render(
        request,
        "crm/target_interaction.html",
        {
            "target_id": target_id,
            "user_id": user_id,
            "user_name": user.username,  # ✅ DB username
            "target_name": get_target_name(target_id),
        },
    )


@require_GET
def moderation_home(request: HttpRequest, moderator_id: str):
    mod = ensure_user(moderator_id)
    if not mod.is_moderator:
        return render(request, "crm/forbidden.html", status=403)

    return render(
        request,
        "crm/moderation_dashboard.html",  # ✅ use the dashboard template
        {
            "moderator_user_id": moderator_id,
            "moderator_username": mod.username,  # ✅ DB username
        },
    )
