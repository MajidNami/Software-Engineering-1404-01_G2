from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def moderator_dashboard(request: HttpRequest):
    moderator_user_id = request.GET.get("moderator_user_id", "")
    return render(request, "crm/moderator_dashboard.html", {"moderator_user_id": moderator_user_id})
