import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from core.jwt_utils import create_access_token, create_refresh_token, decode_token
from core.auth import api_login_required

User = get_user_model()


def _set_auth_cookies(resp: JsonResponse, access: str, refresh: str, settings):
    resp.set_cookie(
        "access_token",
        access,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/",
        max_age=settings.JWT_ACCESS_TTL_SECONDS,
    )
    resp.set_cookie(
        "refresh_token",
        refresh,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/api/auth/",
        max_age=settings.JWT_REFRESH_TTL_SECONDS,
    )


def _clear_auth_cookies(resp: JsonResponse, settings):
    resp.delete_cookie("access_token", path="/")
    resp.delete_cookie("refresh_token", path="/api/auth/")


def health(request):
    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_POST
def signup_api(request):
    from django.conf import settings

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    age_raw = data.get("age")

    if not email:
        return JsonResponse({"error": "email is required"}, status=400)
    if not password:
        return JsonResponse({"error": "password is required"}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"error": "invalid email format"}, status=400)

    try:
        validate_password(password)
    except ValidationError as e:
        return JsonResponse({"error": "invalid password", "details": e.messages}, status=400)

    age = None
    if age_raw not in (None, ""):
        try:
            age = int(age_raw)
        except (TypeError, ValueError):
            return JsonResponse({"error": "age must be an integer"}, status=400)
        if age < 1 or age > 120:
            return JsonResponse({"error": "age must be between 1 and 120"}, status=400)

    # ---- Uniqueness
    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "email already registered"}, status=409)

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        age=age,
    )

    access = create_access_token(user)
    refresh = create_refresh_token(user)

    resp = JsonResponse({
        "ok": True,
        "user": {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age
        }
    })
    _set_auth_cookies(resp, access, refresh, settings)
    return resp


@csrf_exempt
@require_POST
def login_api(request):
    from django.conf import settings

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    if not user.is_active:
        return JsonResponse({"error": "User disabled"}, status=403)

    access = create_access_token(user)
    refresh = create_refresh_token(user)

    resp = JsonResponse({"ok": True, "user": {"email": user.email, "first_name": user.first_name, "last_name": user.last_name, "age": user.age}})
    _set_auth_cookies(resp, access, refresh, settings)
    return resp


@csrf_exempt
@require_POST
def refresh_api(request):
    from django.conf import settings

    rt = request.COOKIES.get("refresh_token")
    if not rt:
        return JsonResponse({"error": "Missing refresh token"}, status=401)

    try:
        payload = decode_token(rt)
        if payload.get("type") != "refresh":
            return JsonResponse({"error": "Invalid token"}, status=401)

        user_id = payload.get("sub")
        tv = payload.get("tv")
        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user or user.token_version != tv:
            return JsonResponse({"error": "Invalid token"}, status=401)

        access = create_access_token(user)
        new_refresh = create_refresh_token(user)

        resp = JsonResponse({"ok": True})
        _set_auth_cookies(resp, access, new_refresh, settings)
        return resp
    except Exception:
        return JsonResponse({"error": "Invalid token"}, status=401)


@csrf_exempt
@require_POST
def logout_api(request):
    from django.conf import settings

    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        user.token_version += 1
        user.save(update_fields=["token_version"])

    resp = JsonResponse({"ok": True})
    _clear_auth_cookies(resp, settings)
    return resp


@api_login_required
def me(request):
    u = request.user
    return JsonResponse({"ok": True, "user": {"email": u.email, "first_name": u.first_name, "last_name": u.last_name, "age": u.age}})


@api_login_required
def verify(request):
    u = request.user
    resp = JsonResponse({"ok": True})
    resp["X-User-Id"] = str(u.id)
    resp["X-User-Email"] = u.email
    resp["X-User-First-Name"] = u.first_name or ""
    resp["X-User-Last-Name"] = u.last_name or ""
    resp["X-User-Age"] = str(u.age or "")
    return resp
