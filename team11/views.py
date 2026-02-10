from django.http import JsonResponse
from django.shortcuts import render, redirect

from core.auth import api_login_required

TEAM_NAME = "team11"

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})

def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

def front(request):
    return redirect(f"http://localhost:9151/api/test/")