from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest

from crm.controllers._http import json_body, ok, handle_service_errors
from crm.services import comments as comments_svc
from crm.services import ratings as ratings_svc
from crm.services import reports as reports_svc
from crm.services import targets as targets_svc
from crm.services import media as media_svc


@csrf_exempt
@require_http_methods(["GET", "POST", "PATCH"])
@handle_service_errors
def comments(request: HttpRequest):
    if request.method == "GET":
        target_id = request.GET.get("target_id") or None
        status = request.GET.get("status") or "all"
        parent_id = request.GET.get("parent_comment_id") or None
        data = comments_svc.get_comments(target_id=target_id, status=status, parent_comment_id=parent_id)
        return ok(data)

    body = json_body(request)

    # PATCH = edit existing comment
    if request.method == "PATCH":
        body = json_body(request)
        user_id = body.get("user_id") or getattr(request.identity, "user_id", None)
        username = body.get("username") or getattr(request.identity, "username", None)

        comment_id = body.get("comment_id")
        new_text = body.get("body")

        updated = comments_svc.edit_comment(
            user_id=user_id,
            username=username,
            comment_id=comment_id,
            body=new_text,
        )
        return ok({
            "id_comment": updated.id_comment,
            "status": updated.status,
            "updated_at": updated.updated_at.isoformat() if updated.updated_at else None,
        })


    # POST = create or replace top-level comment / create reply
    user_id = body.get("user_id") or getattr(request.identity, "user_id", None)
    username = body.get("username") or getattr(request.identity, "username", None)
    target_id = body.get("target_id")
    parent_comment_id = body.get("parent_comment_id")
    text = body.get("body")

    comment = comments_svc.post_comment(
        user_id=user_id,
        username=username,
        target_id=target_id,
        parent_comment_id=parent_comment_id,
        body=text,
    )
    return ok({"id_comment": comment.id_comment, "status": comment.status}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
@handle_service_errors
def comment_status(request: HttpRequest, comment_id: str):
    body = json_body(request)
    status = body.get("status")
    moderator_user_id = (
        body.get("moderator_user_id")
        or getattr(request.identity, "moderator_id", None)
        or getattr(request.identity, "user_id", None)
    )
    moderator_username = body.get("moderator_username") or getattr(request.identity, "username", None)

    comment = comments_svc.update_comment_status(
        moderator_user_id=moderator_user_id,
        moderator_username=moderator_username,
        comment_id=comment_id,
        status=status,
    )
    return ok({"id_comment": comment.id_comment, "status": comment.status})


@csrf_exempt
@require_http_methods(["POST"])
@handle_service_errors
def post_rate(request: HttpRequest):
    body = json_body(request)
    user_id = body.get("user_id") or getattr(request.identity, "user_id", None)
    username = body.get("username") or getattr(request.identity, "username", None)
    target_id = body.get("target_id")
    rating_value = body.get("rating_value")

    aggr = ratings_svc.post_rate(
        user_id=user_id,
        username=username,
        target_id=target_id,
        rating_value=int(rating_value),
    )
    return ok(aggr)


@require_http_methods(["GET"])
@handle_service_errors
def get_avg_rate(request: HttpRequest):
    target_id = request.GET.get("target_id")
    return ok(ratings_svc.get_avg_rate(target_id))


@require_http_methods(["GET"])
@handle_service_errors
def get_my_rate(request: HttpRequest):
    target_id = request.GET.get("target_id")
    user_id = request.GET.get("user_id") or getattr(request.identity, "user_id", None)
    return ok({"rating_value": ratings_svc.get_my_rate(target_id, user_id)})


@csrf_exempt
@require_http_methods(["POST"])
@handle_service_errors
def report(request: HttpRequest):
    body = json_body(request)
    reporter_user_id = body.get("reporter_user_id") or getattr(request.identity, "user_id", None)
    username = body.get("username") or getattr(request.identity, "username", None)
    reason = body.get("reason")
    details = body.get("details")
    media_or_comment = body.get("media_or_comment")
    target_id = body.get("id_media_or_comment")

    rep = reports_svc.create_report(
        reporter_user_id=reporter_user_id,
        username=username,
        reason=reason,
        details=details,
        media_or_comment=int(media_or_comment),
        target_id=target_id,
    )
    return ok({"id_report": rep.id_report, "status": rep.status}, status=201)


@require_http_methods(["GET"])
@handle_service_errors
def pending_reports(request: HttpRequest):
    moderator_user_id = (
        request.GET.get("moderator_user_id")
        or getattr(request.identity, "moderator_id", None)
        or getattr(request.identity, "user_id", None)
    )
    return ok(reports_svc.get_pending_reports(moderator_user_id))


@csrf_exempt
@require_http_methods(["POST"])
@handle_service_errors
def report_status(request: HttpRequest, report_id: str):
    body = json_body(request)
    status = body.get("status")
    moderator_user_id = (
        body.get("moderator_user_id")
        or getattr(request.identity, "moderator_id", None)
        or getattr(request.identity, "user_id", None)
    )

    rep = reports_svc.update_report_status(
        moderator_user_id=moderator_user_id,
        report_id=report_id,
        status=status,
    )
    return ok({"id_report": rep.id_report, "status": rep.status})


@require_http_methods(["GET"])
@handle_service_errors
def target_name(request: HttpRequest, target_id: str):
    return ok({"target_name": targets_svc.get_target_name(target_id)})


@csrf_exempt
@require_http_methods(["GET", "POST"])
@handle_service_errors
def media(request: HttpRequest):
    if request.method == "GET":
        target_id = request.GET.get("target_id")
        status = request.GET.get("status") or "approved"
        return ok(media_svc.list_media(target_id=target_id, status=status))

    # multipart upload
    user_id = request.POST.get("user_id") or getattr(request.identity, "user_id", None)
    username = request.POST.get("username") or getattr(request.identity, "username", None)
    target_id = request.POST.get("target_id")
    media_type = request.POST.get("media_type") or None
    f = request.FILES.get("file")

    m = media_svc.upload_media(
        user_id=user_id,
        username=username,
        target_id=target_id,
        file_obj=f,
        media_type=media_type,
    )
    return ok(
        {"id_media": m.id_media, "status": m.status, "public_url": m.public_url, "media_type": m.media_type},
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
@handle_service_errors
def media_status(request: HttpRequest, media_id: str):
    body = json_body(request)
    status = body.get("status")
    moderator_user_id = (
        body.get("moderator_user_id")
        or getattr(request.identity, "moderator_id", None)
        or getattr(request.identity, "user_id", None)
    )
    m = media_svc.update_media_status(moderator_user_id=moderator_user_id, media_id=media_id, status=status)
    return ok({"id_media": m.id_media, "status": m.status})

@require_http_methods(["POST"])
@handle_service_errors
def media_delete(request: HttpRequest, media_id: str):
    body = json_body(request)
    user_id = body.get("user_id") or getattr(request.identity, "user_id", None)
    media_svc.delete_media(user_id=user_id, media_id=media_id)
    return ok({"id_media": media_id, "deleted": True})

@require_http_methods(["DELETE"])
@handle_service_errors
def media_item(request: HttpRequest, media_id: str):
    user_id = request.GET.get("user_id") or getattr(request.identity, "user_id", None)
    deleted = media_svc.delete_media(user_id=user_id, media_id=media_id)
    return ok({"id_media": deleted.id_media, "deleted": True})


