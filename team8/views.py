from django.http import JsonResponse
from django.shortcuts import render
from core.auth import api_login_required

TEAM_NAME = "team8"

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")