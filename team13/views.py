# مطابق فاز ۳، ۵، ۷ — سرویس امکانات و حمل‌ونقل (گروه Axiom)
import base64
import math
import re
import uuid
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import quote
from django.db.models import Avg, Count, F, Q, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.views.decorators.http import require_GET, require_POST
from core.auth import api_login_required

from .context_processors import team13_user_context
from .neshan.config import get_web_key
from .models import (
    Place,
    PlaceTranslation,
    Event,
    EventTranslation,
    RouteLog,
    RouteContribution,
    Comment,
    Image,
    PlaceContribution,
    TeamAdmin,
)

# پوشهٔ قدیمی برای تصاویر (فقط برای سرو فایل‌های قبلی؛ همهٔ آپلودهای جدید در images_user ذخیره می‌شوند)
CONTRIBUTION_UPLOAD_DIR = Path(__file__).resolve().parent / "contribution_uploads"

TEAM_NAME = "team13"
TEAM13_DB = "team13"  # همهٔ خواندن/نوشتن مکان، رویداد، نظر و ... از دیتابیس SQLite تیم ۱۳


def _wants_json(request):
    """درخواست خروجی JSON (API) دارد یا نه."""
    return (
        request.GET.get("format") == "json"
        or "application/json" in request.headers.get("Accept", "")
    )


def _login_required_team13(view_func):
    """برای درخواست‌های HTML به صفحه ورود با next هدایت می‌کند؛ برای API پاسخ 401."""
    from functools import wraps
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if getattr(request.user, "is_authenticated", False):
            return view_func(request, *args, **kwargs)
        if _wants_json(request):
            return JsonResponse({"detail": "Authentication required"}, status=401)
        login_url = getattr(settings, "LOGIN_URL", "/auth/")
        next_url = request.POST.get("next") or request.GET.get("next") or request.META.get("HTTP_REFERER") or "/team13/"
        if next_url and not url_has_allowed_host_and_scheme(next_url, allowed_hosts=request.get_host(), require_https=request.is_secure()):
            next_url = "/team13/"
        if "?" in login_url:
            redirect_url = f"{login_url}&next={quote(next_url)}"
        else:
            redirect_url = f"{login_url}?next={quote(next_url)}"
        return redirect(redirect_url)
    return _wrapped


def _distance_km(lat1, lon1, lat2, lon2):
    """فاصله تقریبی به کیلومتر (Haversine)."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _team13_context(request, extra=None):
    """یکپارچه: context مشترک همهٔ صفحات team13 (وضعیت کاربر + کلید نقشه)."""
    ctx = team13_user_context(request)
    if extra:
        ctx.update(extra)
    return ctx


@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html", _team13_context(request))


# -----------------------------------------------------------------------------
# مکان‌ها (POI)
# -----------------------------------------------------------------------------

def _parse_lat_lng(request):
    """Parse lat/lng from GET; return (lat, lng) or (None, None) if invalid/missing."""
    lat_s = request.GET.get("lat")
    lng_s = request.GET.get("lng")
    if lat_s is None or lng_s is None:
        return None, None
    try:
        lat = float(lat_s)
        lng = float(lng_s)
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return None, None
        return lat, lng
    except (TypeError, ValueError):
        return None, None


def _apply_price_level_filter(qs, price_level):
    """Filter queryset by price_level (Pricing): 1=budget, 2=mid, 3=high. Applies to hotels (stars) and restaurants (avg_price); other types are included."""
    if not price_level:
        return qs
    level = str(price_level).strip()
    other_types = [Place.PlaceType.MUSEUM, Place.PlaceType.ENTERTAINMENT, Place.PlaceType.HOSPITAL, Place.PlaceType.FIRE_STATION, Place.PlaceType.PHARMACY, Place.PlaceType.CLINIC]
    if level == "1":
        qs = qs.filter(
            Q(type=Place.PlaceType.HOTEL, hotel_details__stars__lte=2)
            | Q(type=Place.PlaceType.FOOD, restaurant_details__avg_price__lte=200000)
            | Q(type__in=other_types)
        )
    elif level == "2":
        qs = qs.filter(
            Q(type=Place.PlaceType.HOTEL, hotel_details__stars=3)
            | Q(
                type=Place.PlaceType.FOOD,
                restaurant_details__avg_price__gt=200000,
                restaurant_details__avg_price__lte=500000,
            )
            | Q(type__in=other_types)
        )
    elif level == "3":
        qs = qs.filter(
            Q(type=Place.PlaceType.HOTEL, hotel_details__stars__gte=4)
            | Q(type=Place.PlaceType.FOOD, restaurant_details__avg_price__gt=500000)
            | Q(type__in=other_types)
        )
    return qs


@require_GET
def place_list(request):
    """
    لیست مکان‌ها از دیتابیس SQLite تیم ۱۳.
    فقط مکان‌های تأییدشده (جدول Place) برگردانده می‌شوند؛ پیشنهادهای در انتظار (PlaceContribution)
    تا پس از تأیید ادمین در این API و نقشه نمایش داده نمی‌شوند.
    فیلتر: نوع/شهر/قیمت؛ فاصله Haversine در صورت ارسال lat/lng.
    """
    # Subquery: average rating (stars) per place from Comment
    rating_subq = (
        Comment.objects.using(TEAM13_DB)
        .filter(
            target_type=Comment.TargetType.PLACE,
            target_id=OuterRef("place_id"),
        )
        .values("target_id")
        .annotate(avg_rating=Avg("rating"))
        .values("avg_rating")
    )
    qs = (
        Place.objects.using(TEAM13_DB)
        .all()
        .select_related("hotel_details", "restaurant_details")
        .prefetch_related("translations")
        .annotate(avg_stars=Coalesce(Subquery(rating_subq), 0.0))
    )
    # Category (Type): type or category GET param
    place_type = request.GET.get("type") or request.GET.get("category")
    if place_type and place_type in dict(Place.PlaceType.choices):
        qs = qs.filter(type=place_type)
    city = request.GET.get("city")
    if city:
        qs = qs.filter(city__icontains=city)
    # Pricing filter
    price_level = request.GET.get("price_level")
    qs = _apply_price_level_filter(qs, price_level)
    # Rating filter (minimum stars)
    min_rating = request.GET.get("min_rating")
    if min_rating is not None:
        try:
            r = float(min_rating)
            if 1 <= r <= 5:
                qs = qs.filter(avg_stars__gte=r)
        except (TypeError, ValueError):
            pass
    # برای نقشه (format=json): صفحه‌بندی و مرتب‌سازی بر اساس نوع و شهر تا بیمارستان/کلینیک/سیرجان و غیره در صفحات اول بیایند.
    max_distance = request.GET.get("max_distance")
    try:
        max_dist_km = float(max_distance) if max_distance else None
    except (TypeError, ValueError):
        max_dist_km = None
    want_all_for_map = _wants_json(request) and not place_type and not city and not price_level and not min_rating
    if want_all_for_map:
        # هر صفحه به‌صورت متناسب از همهٔ انواع مکان (بیمارستان، هتل، غذا، موزه، ...) پر شود
        all_types = [c[0] for c in Place.PlaceType.choices]
        page = max(1, int(request.GET.get("page", 1)))
        page_size = min(500, max(100, int(request.GET.get("page_size", 300))))
        limit_per_type = max(1, page_size // len(all_types))
        start_offset = (page - 1) * limit_per_type
        places_qs = []
        for ptype in all_types:
            type_places = list(
                qs.filter(type=ptype).order_by("city", "place_id")[
                    start_offset : start_offset + limit_per_type
                ]
            )
            places_qs.extend(type_places)
        places_qs.sort(key=lambda p: (p.type, p.city or "", str(p.place_id)))
        places_qs = places_qs[:page_size]
        total_count = qs.count()
        start = (page - 1) * page_size
    else:
        qs = qs.order_by("-avg_stars")
        if max_dist_km is not None:
            places_qs = list(qs[:50])
            total_count = None
        else:
            places_qs = list(qs[:10])
            total_count = None
    place_ids = [p.place_id for p in places_qs]
    rating_rows = (
        Comment.objects.using(TEAM13_DB)
        .filter(
            target_type=Comment.TargetType.PLACE,
            target_id__in=place_ids,
        )
        .values("target_id")
        .annotate(avg_rating=Avg("rating"))
    )
    rating_by_place = {
        str(r["target_id"]): round(float(r["avg_rating"] or 0), 1)
        for r in rating_rows
    }

    user_lat, user_lng = _parse_lat_lng(request)
    places = []
    for p in places_qs:
        trans_fa = p.translations.filter(lang="fa").first()
        trans_en = p.translations.filter(lang="en").first()
        item = {
            "place_id": str(p.place_id),
            "type": p.type,
            "type_display": p.get_type_display(),
            "city": p.city,
            "address": p.address,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "name_fa": trans_fa.name if trans_fa else "",
            "name_en": trans_en.name if trans_en else "",
            "rating": rating_by_place.get(str(p.place_id)),
        }
        if user_lat is not None and user_lng is not None:
            item["distance_km"] = round(_distance_km(user_lat, user_lng, p.latitude, p.longitude), 2)
        places.append(item)

    # Distance filter (when lat/lng present): keep only places within max_distance_km
    if max_dist_km is not None and user_lat is not None and user_lng is not None:
        places = [item for item in places if item.get("distance_km") is not None and item["distance_km"] <= max_dist_km]
    if not want_all_for_map:
        places = places[:10]

    if _wants_json(request):
        payload = {"places": places}
        if total_count is not None:
            page = max(1, int(request.GET.get("page", 1)))
            page_size = min(500, max(100, int(request.GET.get("page_size", 300))))
            payload["total"] = total_count
            payload["page"] = page
            payload["page_size"] = page_size
            payload["has_more"] = (start + len(places_qs)) < total_count
        return JsonResponse(payload)

    return render(request, f"{TEAM_NAME}/places_list.html", _team13_context(request, {
        "places": places,
        "filter_type": place_type or "",
        "filter_city": city or "",
        "filter_min_rating": request.GET.get("min_rating") or "",
        "filter_price_level": request.GET.get("price_level") or "",
        "filter_max_distance": request.GET.get("max_distance") or "",
        "current_lat": user_lat,
        "current_lng": user_lng,
        "is_team13_admin": is_team13_admin(request.user),
    }))


@require_GET
def place_detail(request, place_id):
    """جزئیات یک مکان با ترجمه‌ها، امکانات، جزئیات تخصصی و نظرات/امتیاز (مطابق فاز ۵)."""
    place = get_object_or_404(
        Place.objects.using(TEAM13_DB).select_related("hotel_details", "restaurant_details", "museum_details").prefetch_related("translations", "amenities"),
        place_id=place_id,
    )
    trans_fa = place.translations.filter(lang="fa").first()
    trans_en = place.translations.filter(lang="en").first()
    amenities = list(place.amenities.values_list("amenity_name", flat=True))
    comments = list(
        Comment.objects.using(TEAM13_DB).filter(
            target_type=Comment.TargetType.PLACE, target_id=place.place_id, is_approved=True
        ).order_by("-created_at")[:50]
    )
    images = list(
        Image.objects.using(TEAM13_DB).filter(
            target_type=Image.TargetType.PLACE, target_id=place.place_id, is_approved=True
        ).values_list("image_url", flat=True)
    )

    detail = {
        "place_id": str(place.place_id),
        "type": place.type,
        "type_display": place.get_type_display(),
        "city": place.city,
        "address": place.address,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "name_fa": trans_fa.name if trans_fa else "",
        "name_en": trans_en.name if trans_en else "",
        "description_fa": trans_fa.description if trans_fa else "",
        "description_en": trans_en.description if trans_en else "",
        "amenities": amenities,
        "comments": comments,
        "images": images,
        "is_user_contributed": getattr(place, "is_user_contributed", False),
    }
    if hasattr(place, "hotel_details"):
        detail["hotel"] = {"stars": place.hotel_details.stars, "price_range": place.hotel_details.price_range}
    else:
        detail["hotel"] = None
    if hasattr(place, "restaurant_details"):
        detail["restaurant"] = {"cuisine": place.restaurant_details.cuisine, "avg_price": place.restaurant_details.avg_price}
    else:
        detail["restaurant"] = None
    if hasattr(place, "museum_details"):
        md = place.museum_details
        detail["museum"] = {
            "open_at": str(md.open_at) if md.open_at else None,
            "close_at": str(md.close_at) if md.close_at else None,
            "ticket_price": md.ticket_price,
        }
    else:
        detail["museum"] = None

    if _wants_json(request):
        # میانگین امتیاز فقط از کامنت‌هایی که rating دارند
        ratings_only = [c.rating for c in detail["comments"] if getattr(c, "rating", None) is not None]
        rating_count = len(ratings_only)
        average_rating = round(sum(ratings_only) / rating_count, 1) if rating_count else None
        # خروجی API بدون آبجکت Django
        api = {
            "place_id": detail["place_id"],
            "type": detail["type"],
            "type_display": detail["type_display"],
            "name_fa": detail["name_fa"],
            "name_en": detail["name_en"],
            "city": detail["city"],
            "address": detail["address"],
            "latitude": detail["latitude"],
            "longitude": detail["longitude"],
            "translations": {"fa": {"name": detail["name_fa"], "description": detail["description_fa"]}, "en": {"name": detail["name_en"], "description": detail["description_en"]}},
            "amenities": detail["amenities"],
            "comments": [{"rating": c.rating, "body": getattr(c, "body", "") or "", "created_at": c.created_at.isoformat() if c.created_at else None} for c in detail["comments"]],
            "images": detail["images"],
            "is_user_contributed": detail.get("is_user_contributed", False),
            "average_rating": average_rating,
            "rating_count": rating_count,
        }
        if detail["hotel"]:
            api["hotel"] = detail["hotel"]
        if detail["restaurant"]:
            api["restaurant"] = detail["restaurant"]
        if detail["museum"]:
            api["museum"] = detail["museum"]
        return JsonResponse(api)

    return render(request, f"{TEAM_NAME}/place_detail.html", _team13_context(request, {"place": place, "detail": detail}))


@require_GET
def nearest_place(request):
    """
    نزدیک‌ترین مکان به نقطه (lat, lng) در شعاع radius_km.
    خروجی: { "place": { place_id, name_fa, name_en, type, latitude, longitude, ... } } یا { "place": null }.
    """
    lat, lng = _parse_lat_lng(request)
    if lat is None or lng is None:
        return JsonResponse({"error": "پارامترهای lat و lng الزامی هستند."}, status=400)
    try:
        radius_km = float(request.GET.get("radius_km", "0.05"))
        if radius_km <= 0 or radius_km > 5:
            radius_km = 0.05
    except (TypeError, ValueError):
        radius_km = 0.05
    places = list(Place.objects.using(TEAM13_DB).all())
    best = None
    best_d = float("inf")
    for p in places:
        d = _distance_km(lat, lng, p.latitude, p.longitude)
        if d <= radius_km and d < best_d:
            best_d = d
            best = p
    if best is None:
        return JsonResponse({"place": None})
    trans_fa = best.translations.filter(lang="fa").first()
    trans_en = best.translations.filter(lang="en").first()
    payload = {
        "place_id": str(best.place_id),
        "name_fa": trans_fa.name if trans_fa else "",
        "name_en": trans_en.name if trans_en else "",
        "type": best.type,
        "latitude": best.latitude,
        "longitude": best.longitude,
        "address": best.address or "",
        "distance_km": round(best_d, 4),
    }
    return JsonResponse({"place": payload})


@require_POST
@_login_required_team13
def place_rate(request, place_id):
    """ثبت امتیاز (۱–۵) برای یک مکان. فقط برای کاربران لاگین‌شده."""
    place = get_object_or_404(Place, place_id=place_id)
    try:
        rating = int(request.POST.get("rating", 0))
        if 1 <= rating <= 5:
            Comment.objects.using(TEAM13_DB).create(
                target_type=Comment.TargetType.PLACE,
                target_id=place.place_id,
                rating=rating,
                is_approved=True,
            )
    except (ValueError, TypeError):
        pass
    return redirect("team13:place_detail", place_id=place.place_id)


@require_POST
@_login_required_team13
def place_add_image(request, place_id):
    """افزودن تصویر به یک مکان موجود. فقط برای کاربران لاگین‌شده."""
    place = get_object_or_404(Place, place_id=place_id)
    image_url = None
    if request.FILES and request.FILES.get("image"):
        f = request.FILES["image"]
        content = f.read()
        original_name = getattr(f, "name", None) or ""
        relative_url = _save_image_to_images_user(content, original_name)
        if relative_url:
            image_url = request.build_absolute_uri(relative_url)
    elif request.POST.get("image_base64"):
        raw = request.POST.get("image_base64", "")
        if raw.startswith("data:"):
            raw = raw.split(",", 1)[-1]
        try:
            content = base64.b64decode(raw)
        except Exception:
            content = None
        if content and len(content) < 10 * 1024 * 1024:
            mimetype_hint = (request.POST.get("image_mimetype") or "").strip()
            relative_url = _save_image_to_images_user(content, "image.jpg", mimetype_hint)
            if relative_url:
                image_url = request.build_absolute_uri(relative_url)
    if not image_url:
        return JsonResponse({"error": "تصویری ارسال نشده یا نامعتبر است."}, status=400)
    Image.objects.using(TEAM13_DB).create(
        target_type=Image.TargetType.PLACE,
        target_id=place.place_id,
        image_url=image_url,
        is_approved=False,
    )
    if _wants_json(request):
        return JsonResponse({"ok": True, "message": "تصویر ارسال شد و پس از تأیید ادمین نمایش داده می‌شود."})
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("team13:place_detail", kwargs={"place_id": place.place_id})
    return redirect(next_url + "?msg=" + quote("تصویر ارسال شد و پس از تأیید ادمین نمایش داده می‌شود."))


@require_POST
@_login_required_team13
def place_add_comment(request, place_id):
    """افزودن نظر (متن) و اختیاری امتیاز برای یک مکان. فقط برای کاربران لاگین‌شده."""
    place = get_object_or_404(Place, place_id=place_id)
    body = (request.POST.get("body") or request.POST.get("text") or "").strip()
    rating = None
    try:
        r = int(request.POST.get("rating", 0))
        if 1 <= r <= 5:
            rating = r
    except (ValueError, TypeError):
        pass
    if not body and rating is None:
        return JsonResponse({"error": "متن نظر یا امتیاز الزامی است."}, status=400)
    # نظر متنی فقط پس از تأیید ادمین نمایش داده می‌شود؛ امتیاز تنها فوراً نمایش داده می‌شود
    comment_approved = not (body or "").strip()
    Comment.objects.using(TEAM13_DB).create(
        target_type=Comment.TargetType.PLACE,
        target_id=place.place_id,
        rating=rating,
        body=body or "",
        is_approved=comment_approved,
    )
    if _wants_json(request):
        if comment_approved:
            return JsonResponse({"ok": True, "message": "امتیاز با موفقیت ثبت شد."})
        return JsonResponse({"ok": True, "message": "نظر شما ارسال شد و پس از تأیید ادمین نمایش داده می‌شود."})
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("team13:place_detail", kwargs={"place_id": place.place_id})
    msg = "امتیاز با موفقیت ثبت شد." if comment_approved else "نظر شما ارسال شد و پس از تأیید ادمین نمایش داده می‌شود."
    return redirect(next_url + "?msg=" + quote(msg))


# -----------------------------------------------------------------------------
# پیشنهاد مکان (Place Contribution)
# -----------------------------------------------------------------------------

def _save_contribution_image(upload_dir, file_content, ext=".jpg"):
    """ذخیره در contribution_uploads (فقط برای سازگاری با فایل‌های قدیمی)."""
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}{ext}"
    path = upload_dir / safe_name
    path.write_bytes(file_content)
    return safe_name


def _save_image_to_images_user(file_content, original_filename=None, mimetype_hint=None):
    """
    تصویر را در team13/static/team13/images_user ذخیره می‌کند:
    ابتدا سعی در فشرده‌سازی و خروجی JPEG؛ در صورت خطا ذخیرهٔ خام در همان پوشه.
    برمی‌گرداند: (relative_url برای استفاده با build_absolute_uri) یا None.
    """
    from .image_utils import compress_and_save_image, save_raw_to_images_user

    safe_name, relative_url = compress_and_save_image(file_content, original_filename)
    if relative_url:
        return relative_url
    ext = ".jpg"
    if original_filename:
        suf = Path(original_filename).suffix.lower()
        if suf in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            ext = suf if suf != ".jpeg" else ".jpg"
    if mimetype_hint:
        if "png" in mimetype_hint:
            ext = ".png"
        elif "gif" in mimetype_hint:
            ext = ".gif"
        elif "webp" in mimetype_hint:
            ext = ".webp"
    safe_name, relative_url = save_raw_to_images_user(file_content, ext)
    return relative_url


@require_GET
def serve_contribution_image(request, filename):
    """سرو تصویر آپلود شده پیشنهاد مکان (فقط نام فایل امن)."""
    if not re.match(r"^[a-zA-Z0-9_.-]+$", filename) or ".." in filename:
        raise Http404("Invalid filename")
    path = CONTRIBUTION_UPLOAD_DIR / filename
    if not path.is_file():
        raise Http404("Not found")
    content_type = "image/jpeg"
    if filename.lower().endswith(".png"):
        content_type = "image/png"
    elif filename.lower().endswith(".gif"):
        content_type = "image/gif"
    elif filename.lower().endswith(".webp"):
        content_type = "image/webp"
    return FileResponse(path.open("rb"), content_type=content_type)


@require_POST
@_login_required_team13
def submit_contribution(request):
    """
    ثبت پیشنهاد مکان: name_fa, name_en (اختیاری), type، latitude, longitude (الزامی از نقشه).
    آدرس از کاربر دریافت نمی‌شود؛ همیشه از طول و عرض جغرافیایی به‌صورت خودکار ثابت می‌شود.
    تصویر: multipart (image) یا base64 (image_base64) — اختیاری.
    """
    from .geo_utils import address_from_coords

    name_fa = (request.POST.get("name_fa") or "").strip()
    if not name_fa:
        return JsonResponse({"error": "نام مکان (name_fa) الزامی است."}, status=400)
    name_en = (request.POST.get("name_en") or "").strip()
    place_type = (request.POST.get("type") or "").strip()
    if place_type not in dict(Place.PlaceType.choices):
        place_type = Place.PlaceType.FOOD
    try:
        lat = float(request.POST.get("latitude", 0))
        lng = float(request.POST.get("longitude", 0))
    except (TypeError, ValueError):
        lat, lng = 0.0, 0.0
    if not (-90 <= lat <= 90 and -180 <= lng <= 180) or (lat == 0 and lng == 0):
        return JsonResponse({
            "error": "موقعیت مکانی (طول و عرض جغرافیایی) الزامی است. لطفاً روی نقشه روی موقعیت مورد نظر کلیک کنید و روی دکمهٔ سبز «ادامه» بزنید."
        }, status=400)
    city = (request.POST.get("city") or "").strip()
    address = (request.POST.get("address") or "").strip()
    if not address:
        address = address_from_coords(lat, lng)

    contribution = PlaceContribution.objects.using(TEAM13_DB).create(
        name_fa=name_fa,
        name_en=name_en or name_fa,
        type=place_type,
        address=address,
        latitude=lat,
        longitude=lng,
        city=city,
        submitted_by_id=getattr(request.user, "id", None),
    )
    image_url = None
    # 1) فایل آپلود شده (multipart) — هر فرمت؛ بهینه و ذخیره فقط در images_user
    if request.FILES and request.FILES.get("image"):
        f = request.FILES["image"]
        original_name = getattr(f, "name", None) or ""
        content = f.read()
        relative_url = _save_image_to_images_user(content, original_name)
        if relative_url:
            image_url = request.build_absolute_uri(relative_url)
    # 2) تصویر base64 — بهینه و ذخیره فقط در images_user
    elif request.POST.get("image_base64"):
        raw = request.POST.get("image_base64", "")
        if raw.startswith("data:"):
            raw = raw.split(",", 1)[-1]
        try:
            content = base64.b64decode(raw)
        except Exception:
            content = None
        if content and len(content) < 10 * 1024 * 1024:  # حداکثر 10MB
            mimetype_hint = (request.POST.get("image_mimetype") or "").strip()
            relative_url = _save_image_to_images_user(content, "image.jpg", mimetype_hint)
            if relative_url:
                image_url = request.build_absolute_uri(relative_url)
    if image_url:
        Image.objects.using(TEAM13_DB).create(
            target_type=Image.TargetType.PENDING_PLACE,
            target_id=contribution.contribution_id,
            image_url=image_url,
        )
    if _wants_json(request):
        return JsonResponse({
            "ok": True,
            "contribution_id": str(contribution.contribution_id),
            "message": "پیشنهاد مکان با موفقیت ثبت شد و پس از تأیید در نقشه نمایش داده می‌شود.",
        })
    return JsonResponse({
        "ok": True,
        "contribution_id": str(contribution.contribution_id),
        "message": "پیشنهاد مکان با موفقیت ثبت شد.",
    })


# -----------------------------------------------------------------------------
# پیشنهاد مسیر (Route Contribution) — آدرس از روی عرض/طول ثابت می‌شود
# -----------------------------------------------------------------------------

@require_POST
@_login_required_team13
def submit_route_contribution(request):
    """
    ثبت پیشنهاد مسیر: source_latitude, source_longitude, destination_latitude, destination_longitude, travel_mode.
    آدرس مبدأ و مقصد از روی مختصات (reverse geocode یا فرمت عرض/طول) ثابت و در دیتابیس ذخیره می‌شود.
    پس از تأیید ادمین، دو مکان و یک RouteLog ساخته می‌شود.
    """
    from .geo_utils import address_from_coords

    try:
        src_lat = float(request.POST.get("source_latitude", 0))
        src_lng = float(request.POST.get("source_longitude", 0))
        dst_lat = float(request.POST.get("destination_latitude", 0))
        dst_lng = float(request.POST.get("destination_longitude", 0))
    except (TypeError, ValueError):
        return JsonResponse({"error": "مختصات مبدأ و مقصد (عدد) الزامی است."}, status=400)
    travel_mode = (request.POST.get("travel_mode") or "car").strip().lower()
    if travel_mode not in dict(RouteContribution.TravelMode.choices):
        travel_mode = RouteContribution.TravelMode.CAR
    source_address = address_from_coords(src_lat, src_lng)
    destination_address = address_from_coords(dst_lat, dst_lng)
    user_id = getattr(request.user, "id", None)
    if user_id is not None:
        try:
            user_id = uuid.UUID(str(user_id)) if user_id else None
        except (TypeError, ValueError):
            user_id = None
    rc = RouteContribution.objects.using("team13").create(
        source_address=source_address,
        source_latitude=src_lat,
        source_longitude=src_lng,
        destination_address=destination_address,
        destination_latitude=dst_lat,
        destination_longitude=dst_lng,
        travel_mode=travel_mode,
        user_id=user_id,
    )
    return JsonResponse({
        "ok": True,
        "contribution_id": str(rc.contribution_id),
        "message": "پیشنهاد مسیر ثبت شد و پس از تأیید ادمین در سیستم ذخیره می‌شود.",
    })


# -----------------------------------------------------------------------------
# پنل ادمین تیم ۱۳ (فقط برای کاربران TeamAdmin)
# -----------------------------------------------------------------------------

def is_team13_admin(user):
    """بررسی اینکه کاربر در جدول TeamAdmin باشد یا سوپریوزر باشد."""
    if not getattr(user, "is_authenticated", False):
        return False
    return (
        TeamAdmin.objects.using("team13").filter(user_id=str(user.id)).exists()
        or getattr(user, "is_superuser", False)
    )


def _is_team13_admin(user):
    """Alias for is_team13_admin (backward compatibility)."""
    return is_team13_admin(user)


def team13_admin_dashboard(request):
    """داشبورد ادمین: لیست پیشنهادهای در انتظار تأیید و مدیریت ادمین‌ها."""
    if not getattr(request.user, "is_authenticated", False):
        login_url = getattr(settings, "LOGIN_URL", "/auth/")
        next_url = request.get_full_path()
        if next_url and not url_has_allowed_host_and_scheme(next_url, allowed_hosts=request.get_host(), require_https=request.is_secure()):
            next_url = "/team13/admin/"
        if "?" in login_url:
            redirect_url = f"{login_url}&next={quote(next_url)}"
        else:
            redirect_url = f"{login_url}?next={quote(next_url)}"
        return redirect(redirect_url)
    if not is_team13_admin(request.user):
        login_url = getattr(settings, "LOGIN_URL", "/auth/")
        next_url = quote(request.get_full_path())
        return HttpResponseForbidden(
            '<!DOCTYPE html><html dir="rtl" lang="fa"><head><meta charset="utf-8"><title>دسترسی غیرمجاز</title></head><body style="font-family:tahoma;padding:2rem;max-width:500px;margin:0 auto;">'
            '<h1>۴۰۳ — دسترسی غیرمجاز</h1>'
            '<p>دسترسی به پنل ادمین تیم ۱۳ فقط برای کاربران تعریف‌شده به‌عنوان ادمین امکان‌پذیر است.</p>'
            '<p>با حساب <strong>admin@gmail.com</strong> و رمز <strong>admin</strong> وارد شوید (پس از اجرای migrate این کاربر به‌صورت خودکار ادمین تیم ۱۳ است).</p>'
            '<p><a href="' + login_url + '?next=' + next_url + '" style="display:inline-block;margin-top:12px;padding:10px 20px;background:#1b4332;color:#fff;border-radius:8px;text-decoration:none;">ورود به سامانه</a></p>'
            '</body></html>'
        )

    # پیشنهادهای در انتظار (pending = is_approved=False) از دیتابیس team13
    pending = PlaceContribution.objects.using("team13").filter(is_approved=False).order_by("-created_at")
    pending_requests = []
    for c in pending:
        images = list(
            Image.objects.using("team13").filter(
                target_type=Image.TargetType.PENDING_PLACE,
                target_id=c.contribution_id,
            ).values_list("image_url", flat=True)
        )
        map_url = (
            reverse("team13:index")
            + "?lat={}&lng={}&zoom=16".format(c.latitude, c.longitude)
        )
        submitter_display = "—"
        if c.submitted_by_id:
            try:
                User = request.user.__class__
                sub = User.objects.using("default").filter(id=c.submitted_by_id).first()
                submitter_display = getattr(sub, "email", str(c.submitted_by_id)) if sub else str(c.submitted_by_id)
            except Exception:
                submitter_display = str(c.submitted_by_id)
        pending_requests.append({
            "contribution": c,
            "images": images,
            "map_url": map_url,
            "submitter_display": submitter_display,
        })

    pending_routes = list(
        RouteContribution.objects.using("team13").filter(is_approved=False).order_by("-created_at")
    )

    pending_comments_list_raw = list(
        Comment.objects.using("team13").filter(
            target_type=Comment.TargetType.PLACE, is_approved=False
        ).order_by("-created_at")
    )
    place_ids_comments = list({c.target_id for c in pending_comments_list_raw})
    places_for_comments = {
        str(p.place_id): (p.translations.filter(lang="fa").first() or p.translations.filter(lang="en").first())
        for p in Place.objects.using("team13").filter(place_id__in=place_ids_comments).prefetch_related("translations")
    }
    pending_comments_list = []
    for c in pending_comments_list_raw:
        trans = places_for_comments.get(str(c.target_id))
        place_name = trans.name if trans else str(c.target_id)
        pending_comments_list.append({"comment": c, "place_name": place_name})

    pending_images_list_raw = list(
        Image.objects.using("team13").filter(
            target_type=Image.TargetType.PLACE, is_approved=False
        ).order_by("image_id")
    )
    place_ids_images = list({img.target_id for img in pending_images_list_raw})
    places_for_images = {
        str(p.place_id): (p.translations.filter(lang="fa").first() or p.translations.filter(lang="en").first())
        for p in Place.objects.using("team13").filter(place_id__in=place_ids_images).prefetch_related("translations")
    }
    pending_images_list = []
    for img in pending_images_list_raw:
        trans = places_for_images.get(str(img.target_id))
        place_name = trans.name if trans else str(img.target_id)
        pending_images_list.append({"image": img, "place_name": place_name})

    return render(request, f"{TEAM_NAME}/admin_dashboard.html", _team13_context(request, {
        "pending_requests": pending_requests,
        "contributions_with_images": pending_requests,
        "pending_route_contributions": pending_routes,
        "pending_comments": pending_comments_list,
        "pending_images": pending_images_list,
        "map_index_url": reverse("team13:index"),
    }))


@require_POST
def team13_admin_approve(request, contribution_id):
    """تأیید یک پیشنهاد مکان (فقط ادمین)."""
    if not getattr(request.user, "is_authenticated", False):
        return HttpResponseForbidden("Authentication required")
    if not is_team13_admin(request.user):
        return HttpResponseForbidden("Forbidden")
    from .moderation import approve_contribution
    try:
        approve_contribution(contribution_id)
    except PlaceContribution.DoesNotExist:
        pass
    return redirect("team13:team13_admin_panel")


@require_POST
def team13_admin_reject(request, contribution_id):
    """رد یک پیشنهاد مکان و حذف آن (فقط ادمین)."""
    if not getattr(request.user, "is_authenticated", False):
        return HttpResponseForbidden("Authentication required")
    if not is_team13_admin(request.user):
        return HttpResponseForbidden("Forbidden")
    contribution = PlaceContribution.objects.using("team13").filter(contribution_id=contribution_id).first()
    if contribution:
        Image.objects.using("team13").filter(
            target_type=Image.TargetType.PENDING_PLACE,
            target_id=contribution.contribution_id,
        ).delete()
        contribution.delete()
    return redirect("team13:team13_admin_panel")


@require_POST
def team13_admin_approve_route(request, contribution_id):
    """تأیید یک پیشنهاد مسیر (فقط ادمین)."""
    if not getattr(request.user, "is_authenticated", False):
        return HttpResponseForbidden("Authentication required")
    if not is_team13_admin(request.user):
        return HttpResponseForbidden("Forbidden")
    from .moderation import approve_route_contribution
    try:
        approve_route_contribution(contribution_id)
    except RouteContribution.DoesNotExist:
        pass
    return redirect("team13:team13_admin_panel")


@require_POST
def team13_admin_reject_route(request, contribution_id):
    """رد یک پیشنهاد مسیر و حذف آن (فقط ادمین)."""
    if not getattr(request.user, "is_authenticated", False):
        return HttpResponseForbidden("Authentication required")
    if not is_team13_admin(request.user):
        return HttpResponseForbidden("Forbidden")
    rc = RouteContribution.objects.using("team13").filter(contribution_id=contribution_id).first()
    if rc:
        rc.delete()
    return redirect("team13:team13_admin_panel")


@require_POST
def team13_admin_approve_comment(request, comment_id):
    """تأیید یک نظر — پس از تأیید برای همه نمایش داده می‌شود."""
    if not getattr(request.user, "is_authenticated", False):
        return HttpResponseForbidden("Authentication required")
    if not is_team13_admin(request.user):
        return HttpResponseForbidden("Forbidden")
    Comment.objects.using("team13").filter(comment_id=comment_id).update(is_approved=True)
    return redirect("team13:team13_admin_panel")


@require_POST
def team13_admin_reject_comment(request, comment_id):
    """رد و حذف یک نظر."""
    if not getattr(request.user, "is_authenticated", False):
        return HttpResponseForbidden("Authentication required")
    if not is_team13_admin(request.user):
        return HttpResponseForbidden("Forbidden")
    Comment.objects.using("team13").filter(comment_id=comment_id).delete()
    return redirect("team13:team13_admin_panel")


@require_POST
def team13_admin_approve_image(request, image_id):
    """تأیید یک تصویر — پس از تأیید برای همه نمایش داده می‌شود."""
    if not getattr(request.user, "is_authenticated", False):
        return HttpResponseForbidden("Authentication required")
    if not is_team13_admin(request.user):
        return HttpResponseForbidden("Forbidden")
    Image.objects.using("team13").filter(image_id=image_id).update(is_approved=True)
    return redirect("team13:team13_admin_panel")


@require_POST
def team13_admin_reject_image(request, image_id):
    """رد و حذف یک تصویر."""
    if not getattr(request.user, "is_authenticated", False):
        return HttpResponseForbidden("Authentication required")
    if not is_team13_admin(request.user):
        return HttpResponseForbidden("Forbidden")
    Image.objects.using("team13").filter(image_id=image_id).delete()
    return redirect("team13:team13_admin_panel")


@require_POST
def team13_admin_add_admin(request):
    """افزودن کاربر به جدول ادمین‌ها با ایمیل (فقط ادمین فعلی)."""
    if not getattr(request.user, "is_authenticated", False):
        return HttpResponseForbidden("Authentication required")
    if not is_team13_admin(request.user):
        return HttpResponseForbidden("Forbidden")
    User = request.user.__class__
    email = (request.POST.get("email") or "").strip().lower()
    if not email:
        return redirect("team13:team13_admin_panel")
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return redirect("team13:team13_admin_panel")
    TeamAdmin.objects.using("team13").get_or_create(
        user_id=str(user.id),
        defaults={"user_id": str(user.id)},
    )
    return redirect("team13:team13_admin_panel")


# -----------------------------------------------------------------------------
# رویدادها
# -----------------------------------------------------------------------------

@require_GET
def event_list(request):
    """لیست رویدادها از دیتابیس team13. فیلتر شهر با GET city=. خروجی: JSON (API) یا صفحه HTML."""
    qs = Event.objects.using(TEAM13_DB).all().prefetch_related("translations").order_by("-start_at")
    city = (request.GET.get("city") or "").strip()
    if city:
        qs = qs.filter(city__icontains=city)
    qs = qs[:100]
    events = []
    for e in qs:
        trans_fa = e.translations.filter(lang="fa").first()
        trans_en = e.translations.filter(lang="en").first()
        events.append({
            "event_id": str(e.event_id),
            "city": e.city,
            "address": e.address,
            "latitude": e.latitude,
            "longitude": e.longitude,
            "start_at": e.start_at,
            "end_at": e.end_at,
            "start_at_iso": e.start_at.isoformat(),
            "end_at_iso": e.end_at.isoformat(),
            "title_fa": trans_fa.title if trans_fa else "",
            "title_en": trans_en.title if trans_en else "",
            "description_fa": trans_fa.description if trans_fa else "",
        })

    if _wants_json(request):
        return JsonResponse({
            "events": [
                {
                    "event_id": x["event_id"],
                    "city": x["city"],
                    "latitude": x.get("latitude"),
                    "longitude": x.get("longitude"),
                    "start_at": x["start_at_iso"],
                    "end_at": x.get("end_at_iso"),
                    "title_fa": x["title_fa"],
                }
                for x in events
            ]
        })

    return render(request, f"{TEAM_NAME}/events_list.html", _team13_context(request, {"events": events}))


@require_GET
def event_detail(request, event_id):
    """جزئیات یک رویداد با ترجمه‌ها و نظرات/امتیاز."""
    event = get_object_or_404(
        Event.objects.using(TEAM13_DB).prefetch_related("translations"),
        event_id=event_id,
    )
    trans_fa = event.translations.filter(lang="fa").first()
    trans_en = event.translations.filter(lang="en").first()
    comments = list(
        Comment.objects.using(TEAM13_DB).filter(target_type=Comment.TargetType.EVENT, target_id=event.event_id)
        .order_by("-created_at")[:50]
    )
    images = list(
        Image.objects.using(TEAM13_DB).filter(target_type=Image.TargetType.EVENT, target_id=event.event_id)
        .values_list("image_url", flat=True)
    )

    detail = {
        "event_id": str(event.event_id),
        "city": event.city,
        "address": event.address,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "start_at": event.start_at,
        "end_at": event.end_at,
        "title_fa": trans_fa.title if trans_fa else "",
        "title_en": trans_en.title if trans_en else "",
        "description_fa": trans_fa.description if trans_fa else "",
        "description_en": trans_en.description if trans_en else "",
        "comments": comments,
        "images": images,
    }

    if _wants_json(request):
        return JsonResponse({
            **detail,
            "start_at": event.start_at.isoformat(),
            "end_at": event.end_at.isoformat(),
            "comments": [{"rating": c.rating, "created_at": c.created_at.isoformat() if c.created_at else None} for c in comments],
        })

    return render(request, f"{TEAM_NAME}/event_detail.html", _team13_context(request, {"event": event, "detail": detail}))


@require_POST
@_login_required_team13
def event_rate(request, event_id):
    """ثبت امتیاز (۱–۵) برای یک رویداد. فقط برای کاربران لاگین‌شده."""
    event = get_object_or_404(Event, event_id=event_id)
    try:
        rating = int(request.POST.get("rating", 0))
        if 1 <= rating <= 5:
            Comment.objects.using(TEAM13_DB).create(
                target_type=Comment.TargetType.EVENT,
                target_id=event.event_id,
                rating=rating,
            )
    except (ValueError, TypeError):
        pass
    return redirect("team13:event_detail", event_id=event.event_id)


# -----------------------------------------------------------------------------
# مسیریابی و امکانات روی مسیر (در صورت تنظیم نشان از API نشان؛ وگرنه Haversine)
# -----------------------------------------------------------------------------

def _compute_route_result(source, dest, travel_mode, request, **route_options):
    """محاسبه فاصله و ETA؛ برای خودرو/موتور در صورت وجود کلید نشان از API نشان استفاده می‌شود.
    route_options: vehicle_type, avoid_traffic_zone, avoid_odd_even_zone, alternative (برای fetch_route_eta).
    """
    dist_km = _distance_km(source.latitude, source.longitude, dest.latitude, dest.longitude)
    eta_minutes = None
    eta_source = "haversine"

    route_geometry = None
    if travel_mode in ("car", "motorcycle"):
        try:
            no_traffic = route_options.get("no_traffic", False)
            bearing = route_options.get("bearing")
            if travel_mode == "car" and no_traffic:
                from .neshan import fetch_route_eta_no_traffic
                dist_neshan, dur_sec, route_geometry = fetch_route_eta_no_traffic(
                    source.longitude, source.latitude, dest.longitude, dest.latitude,
                    avoid_traffic_zone=route_options.get("avoid_traffic_zone", False),
                    avoid_odd_even_zone=route_options.get("avoid_odd_even_zone", False),
                    alternative=route_options.get("alternative", False),
                    bearing=bearing,
                )
                eta_source = "neshan_no_traffic"
            else:
                from .neshan import fetch_route_eta
                vehicle_type = route_options.get("vehicle_type") or ("motorcycle" if travel_mode == "motorcycle" else "car")
                dist_neshan, dur_sec, route_geometry = fetch_route_eta(
                    source.longitude, source.latitude,
                    dest.longitude, dest.latitude,
                    vehicle_type=vehicle_type,
                    avoid_traffic_zone=route_options.get("avoid_traffic_zone", False),
                    avoid_odd_even_zone=route_options.get("avoid_odd_even_zone", False),
                    alternative=route_options.get("alternative", False),
                    bearing=bearing,
                )
                eta_source = "neshan"
            if dist_neshan is not None and dur_sec is not None:
                dist_km = dist_neshan
                eta_minutes = max(1, round(dur_sec / 60.0))
            else:
                eta_minutes = max(1, round(dist_km / 0.5))
        except Exception:
            eta_minutes = max(1, round(dist_km / 0.5))
    elif travel_mode == "walk":
        try:
            from .neshan import fetch_route_eta_pedestrian
            bearing = route_options.get("bearing")
            dist_neshan, dur_sec, route_geometry = fetch_route_eta_pedestrian(
                source.longitude, source.latitude, dest.longitude, dest.latitude,
                alternative=route_options.get("alternative", False),
                bearing=bearing,
            )
            if dist_neshan is not None and dur_sec is not None:
                dist_km = dist_neshan
                eta_minutes = max(1, round(dur_sec / 60.0))
                eta_source = "neshan_pedestrian"
            else:
                eta_minutes = max(1, round(dist_km / 0.08))
        except Exception:
            eta_minutes = max(1, round(dist_km / 0.08))
    else:
        eta_minutes = max(1, round(dist_km / 0.4))

    trans_src = source.translations.filter(lang="fa").first()
    trans_dst = dest.translations.filter(lang="fa").first()
    result = {
        "source_place_id": str(source.place_id),
        "destination_place_id": str(dest.place_id),
        "source_name": trans_src.name if trans_src else str(source.place_id),
        "destination_name": trans_dst.name if trans_dst else str(dest.place_id),
        "travel_mode": travel_mode,
        "distance_km": round(dist_km, 2),
        "eta_minutes": eta_minutes,
        "eta_source": eta_source,
        "source_amenities": list(source.amenities.values_list("amenity_name", flat=True)),
        "destination_amenities": list(dest.amenities.values_list("amenity_name", flat=True)),
        "source_lat": source.latitude,
        "source_lng": source.longitude,
        "dest_lat": dest.latitude,
        "dest_lng": dest.longitude,
    }
    if route_geometry is not None:
        result["route_geometry"] = route_geometry
    return result


def _compute_route_result_from_coords(lat_src, lng_src, name_src, lat_dest, lng_dest, name_dest, travel_mode, **route_options):
    """محاسبه فاصله و ETA از روی مختصات؛ برای خودرو/موتور در صورت وجود نشان از API نشان."""
    dist_km = _distance_km(lat_src, lng_src, lat_dest, lng_dest)
    eta_minutes = None
    eta_source = "haversine"

    route_geometry = None
    if travel_mode in ("car", "motorcycle"):
        try:
            no_traffic = route_options.get("no_traffic", False)
            bearing = route_options.get("bearing")
            if travel_mode == "car" and no_traffic:
                from .neshan import fetch_route_eta_no_traffic
                dist_neshan, dur_sec, route_geometry = fetch_route_eta_no_traffic(
                    lng_src, lat_src, lng_dest, lat_dest,
                    avoid_traffic_zone=route_options.get("avoid_traffic_zone", False),
                    avoid_odd_even_zone=route_options.get("avoid_odd_even_zone", False),
                    alternative=route_options.get("alternative", False),
                    bearing=bearing,
                )
                eta_source = "neshan_no_traffic"
            else:
                from .neshan import fetch_route_eta
                vehicle_type = route_options.get("vehicle_type") or ("motorcycle" if travel_mode == "motorcycle" else "car")
                dist_neshan, dur_sec, route_geometry = fetch_route_eta(
                    lng_src, lat_src, lng_dest, lat_dest,
                    vehicle_type=vehicle_type,
                    avoid_traffic_zone=route_options.get("avoid_traffic_zone", False),
                    avoid_odd_even_zone=route_options.get("avoid_odd_even_zone", False),
                    alternative=route_options.get("alternative", False),
                    bearing=bearing,
                )
                eta_source = "neshan"
            if dist_neshan is not None and dur_sec is not None:
                dist_km = dist_neshan
                eta_minutes = max(1, round(dur_sec / 60.0))
            else:
                eta_minutes = max(1, round(dist_km / 0.5))
        except Exception:
            eta_minutes = max(1, round(dist_km / 0.5))
    elif travel_mode == "walk":
        try:
            from .neshan import fetch_route_eta_pedestrian
            bearing = route_options.get("bearing")
            dist_neshan, dur_sec, route_geometry = fetch_route_eta_pedestrian(
                lng_src, lat_src, lng_dest, lat_dest,
                alternative=route_options.get("alternative", False),
                bearing=bearing,
            )
            if dist_neshan is not None and dur_sec is not None:
                dist_km = dist_neshan
                eta_minutes = max(1, round(dur_sec / 60.0))
                eta_source = "neshan_pedestrian"
            else:
                eta_minutes = max(1, round(dist_km / 0.08))
        except Exception:
            eta_minutes = max(1, round(dist_km / 0.08))
    else:
        eta_minutes = max(1, round(dist_km / 0.4))

    result = {
        "source_name": name_src or "مبدأ",
        "destination_name": name_dest or "مقصد",
        "travel_mode": travel_mode,
        "distance_km": round(dist_km, 2),
        "eta_minutes": eta_minutes,
        "eta_source": eta_source,
        "source_amenities": [],
        "destination_amenities": [],
        "source_lat": lat_src,
        "source_lng": lng_src,
        "dest_lat": lat_dest,
        "dest_lng": lng_dest,
    }
    if route_geometry is not None:
        result["route_geometry"] = route_geometry
    return result


@require_GET
def route_request(request):
    """
    مسیریابی و ETA بین دو مکان + امکانات مبدأ و مقصد.
    پذیرش: source_place_id/destination_place_id (مکان از دیتابیس) یا
    source_lat, source_lng, source_name, dest_lat, dest_lng, dest_name (جستجوی آدرس).
    """
    src_id = request.GET.get("source_place_id")
    dst_id = request.GET.get("destination_place_id")
    source_lat = request.GET.get("source_lat")
    source_lng = request.GET.get("source_lng")
    source_name = request.GET.get("source_name", "")
    dest_lat = request.GET.get("dest_lat")
    dest_lng = request.GET.get("dest_lng")
    dest_name = request.GET.get("dest_name", "")
    travel_mode = request.GET.get("travel_mode", "car").lower()
    if travel_mode not in ("car", "walk", "transit", "motorcycle"):
        travel_mode = "car"
    # پارامترهای اختیاری API مسیریابی نشان (v4)
    vehicle_type = request.GET.get("vehicle_type", "").lower().strip() or None
    if vehicle_type and vehicle_type not in ("car", "motorcycle"):
        vehicle_type = None
    avoid_traffic_zone = request.GET.get("avoid_traffic_zone", "").lower() in ("1", "true", "yes")
    avoid_odd_even_zone = request.GET.get("avoid_odd_even_zone", "").lower() in ("1", "true", "yes")
    alternative = request.GET.get("alternative", "").lower() in ("1", "true", "yes")
    no_traffic = request.GET.get("no_traffic", "").lower() in ("1", "true", "yes")
    try:
        bearing = int(request.GET.get("bearing", ""))
        if not (0 <= bearing <= 360):
            bearing = None
    except (TypeError, ValueError):
        bearing = None
    route_options = {
        "vehicle_type": vehicle_type,
        "avoid_traffic_zone": avoid_traffic_zone,
        "avoid_odd_even_zone": avoid_odd_even_zone,
        "alternative": alternative,
        "no_traffic": no_traffic,
        "bearing": bearing,
    }

    if _wants_json(request):
        if src_id and dst_id:
            try:
                source = Place.objects.using(TEAM13_DB).prefetch_related("translations", "amenities").get(place_id=src_id)
                dest = Place.objects.using(TEAM13_DB).prefetch_related("translations", "amenities").get(place_id=dst_id)
                result = _compute_route_result(source, dest, travel_mode, request, **route_options)
                if getattr(request.user, "is_authenticated", False):
                    try:
                        RouteLog.objects.using(TEAM13_DB).create(
                            user_id=getattr(request.user, "id", None),
                            source_place=source,
                            destination_place=dest,
                            travel_mode=travel_mode,
                        )
                    except Exception:
                        pass
                return JsonResponse(result)
            except Place.DoesNotExist:
                return JsonResponse({"error": "مکان مبدأ یا مقصد یافت نشد"}, status=404)
        if source_lat and source_lng and dest_lat and dest_lng:
            try:
                lat_s = float(source_lat)
                lng_s = float(source_lng)
                lat_d = float(dest_lat)
                lng_d = float(dest_lng)
                result = _compute_route_result_from_coords(
                    lat_s, lng_s, source_name, lat_d, lng_d, dest_name, travel_mode, **route_options
                )
                return JsonResponse(result)
            except (TypeError, ValueError):
                pass
        return JsonResponse({"error": "source_place_id و destination_place_id یا source_lat/lng و dest_lat/lng الزامی است"}, status=400)

    # صفحه HTML
    route_result = None
    if source_lat and source_lng and dest_lat and dest_lng:
        try:
            lat_s = float(source_lat)
            lng_s = float(source_lng)
            lat_d = float(dest_lat)
            lng_d = float(dest_lng)
            route_result = _compute_route_result_from_coords(
                lat_s, lng_s, source_name, lat_d, lng_d, dest_name, travel_mode, **route_options
            )
        except (TypeError, ValueError):
            route_result = {"error": "مختصات مبدأ یا مقصد نامعتبر است."}
    elif src_id and dst_id:
        try:
            source = Place.objects.using(TEAM13_DB).prefetch_related("translations", "amenities").get(place_id=src_id)
            dest = Place.objects.using(TEAM13_DB).prefetch_related("translations", "amenities").get(place_id=dst_id)
            route_result = _compute_route_result(source, dest, travel_mode, request, **route_options)
            if getattr(request.user, "is_authenticated", False):
                try:
                    RouteLog.objects.using(TEAM13_DB).create(
                        user_id=getattr(request.user, "id", None),
                        source_place=source,
                        destination_place=dest,
                        travel_mode=travel_mode,
                    )
                except Exception:
                    pass
        except Place.DoesNotExist:
            route_result = {"error": "مکان مبدأ یا مقصد یافت نشد."}

    places_choices = list(Place.objects.using(TEAM13_DB).all().prefetch_related("translations")[:200])
    places_for_select = []
    for p in places_choices:
        t = p.translations.filter(lang="fa").first()
        name = (t.name if t else None) or (p.translations.filter(lang="en").first().name if p.translations.filter(lang="en").first() else None) or str(p.place_id)
        places_for_select.append({"place_id": str(p.place_id), "name": name})

    return render(request, f"{TEAM_NAME}/routes.html", _team13_context(request, {
        "route_result": route_result,
        "places_for_select": places_for_select,
        "travel_mode": travel_mode,
        "source_place_id": src_id or "",
        "destination_place_id": dst_id or "",
    }))


# -----------------------------------------------------------------------------
# مسیریابی فروشنده دوره‌گرد (TSP) — بهینه‌سازی ترتیب بازدید از چند نقطه
# مستندات: https://platform.neshan.org/docs/api/routing-category/tsp/
# -----------------------------------------------------------------------------

@require_GET
def tsp_request(request):
    """
    بهینه‌سازی ترتیب بازدید از چند نقطه (TSP).
    GET: waypoints (اجباری) = lat1,lng1|lat2,lng2|... یا چند waypoints=lat,lng
         round_trip، source_is_any_point، last_is_any_point (اختیاری، true/false).
    پاسخ JSON: { "points": [ { "name", "location": [lng, lat], "index" }, ... ] } یا { "error": "..." }.
    """
    waypoints_raw = request.GET.get("waypoints", "").strip()
    if not waypoints_raw:
        # چند پارامتر waypoints
        waypoints_list = request.GET.getlist("waypoints")
        waypoints_raw = "|".join(p.strip() for p in waypoints_list if p.strip())
    if not waypoints_raw or waypoints_raw.count("|") < 1:
        if _wants_json(request):
            return JsonResponse({"error": "پارامتر waypoints الزامی است (حداقل دو نقطه به صورت lat,lng|lat,lng)"}, status=400)
        return JsonResponse({"error": "پارامتر waypoints الزامی است (حداقل دو نقطه به صورت lat,lng|lat,lng)"}, status=400)

    round_trip = request.GET.get("round_trip", "true").lower() in ("1", "true", "yes")
    source_is_any = request.GET.get("source_is_any_point", "true").lower() in ("1", "true", "yes")
    last_is_any = request.GET.get("last_is_any_point", "true").lower() in ("1", "true", "yes")

    try:
        from .neshan import fetch_tsp
        points = fetch_tsp(
            waypoints_raw,
            round_trip=round_trip,
            source_is_any_point=source_is_any,
            last_is_any_point=last_is_any,
        )
    except Exception as e:
        if _wants_json(request):
            return JsonResponse({"error": "خطا در فراخوانی سرویس بهینه‌سازی مسیر"}, status=500)
        return JsonResponse({"error": "خطا در فراخوانی سرویس بهینه‌سازی مسیر"}, status=500)

    if points is None:
        if _wants_json(request):
            return JsonResponse({"error": "سرویس بهینه‌سازی مسیر در دسترس نیست یا پاسخ نامعتبر"}, status=502)
        return JsonResponse({"error": "سرویس بهینه‌سازی مسیر در دسترس نیست یا پاسخ نامعتبر"}, status=502)

    if _wants_json(request):
        return JsonResponse({"points": points})
    return JsonResponse({"points": points})


# -----------------------------------------------------------------------------
# ماتریس فاصله (Distance Matrix) — فاصله و زمان بین چند مبدأ و چند مقصد
# مستندات: https://platform.neshan.org/docs/api/routing-category/distance-matrix/
# -----------------------------------------------------------------------------

@require_GET
def distance_matrix_request(request):
    """
    ماتریس فاصله و زمان بین نقاط مبدأ و مقصد.
    GET: origins (اجباری) = lat1,lng1|lat2,lng2|... ، destinations (اجباری) همان فرمت.
         type = car | motorcycle (اختیاری)، no_traffic = 0|1|true|false (اختیاری).
    پاسخ JSON: { status, rows, origin_addresses, destination_addresses } یا { "error": "..." }.
    """
    origins_raw = request.GET.get("origins", "").strip()
    destinations_raw = request.GET.get("destinations", "").strip()
    if not origins_raw:
        origins_list = request.GET.getlist("origins")
        origins_raw = "|".join(p.strip() for p in origins_list if p.strip())
    if not destinations_raw:
        dest_list = request.GET.getlist("destinations")
        destinations_raw = "|".join(p.strip() for p in dest_list if p.strip())
    if not origins_raw or not destinations_raw:
        return JsonResponse(
            {"error": "پارامترهای origins و destinations الزامی هستند (مختصات به صورت lat,lng با جداکننده |)"},
            status=400,
        )
    vehicle_type = request.GET.get("type", "car").lower().strip()
    if vehicle_type not in ("car", "motorcycle"):
        vehicle_type = "car"
    no_traffic = request.GET.get("no_traffic", "").lower() in ("1", "true", "yes")
    try:
        from .neshan import fetch_distance_matrix
        data = fetch_distance_matrix(
            origins_raw,
            destinations_raw,
            vehicle_type=vehicle_type,
            no_traffic=no_traffic,
        )
    except Exception:
        return JsonResponse({"error": "خطا در فراخوانی سرویس ماتریس فاصله"}, status=500)
    if data is None:
        return JsonResponse({"error": "سرویس ماتریس فاصله در دسترس نیست یا پاسخ نامعتبر"}, status=502)
    return JsonResponse(data)


# -----------------------------------------------------------------------------
# محدوده در دسترس (Isochrone) — محدوده قابل دسترسی بر اساس زمان یا مسافت
# مستندات: https://platform.neshan.org/docs/api/routing-category/isochrone/
# -----------------------------------------------------------------------------

@require_GET
def isochrone_request(request):
    """
    محدوده‌ای که از نقطه مرکز در زمان یا مسافت معین قابل دسترسی است.
    GET: location=lat,lng یا lat و lng جداگانه؛ distance (کیلومتر) و/یا time (دقیقه) — حداقل یکی اجباری.
         polygon = true|false (اختیاری)، denoise = 0..1 (اختیاری).
    پاسخ: GeoJSON FeatureCollection یا { "error": "..." }.
    """
    location_raw = request.GET.get("location", "").strip()
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    if location_raw and "," in location_raw:
        parts = location_raw.split(",", 1)
        try:
            lat = lat or parts[0].strip()
            lng = lng or parts[1].strip()
        except IndexError:
            pass
    try:
        lat_f = float(lat) if lat else None
        lng_f = float(lng) if lng else None
    except (TypeError, ValueError):
        lat_f = lng_f = None
    if lat_f is None or lng_f is None:
        return JsonResponse(
            {"error": "پارامتر location (lat,lng) یا lat و lng الزامی است"},
            status=400,
        )
    distance_raw = request.GET.get("distance", "").strip()
    time_raw = request.GET.get("time", "").strip()
    distance_km = None
    if distance_raw:
        try:
            distance_km = float(distance_raw)
        except (TypeError, ValueError):
            pass
    time_minutes = None
    if time_raw:
        try:
            time_minutes = float(time_raw)
        except (TypeError, ValueError):
            pass
    if distance_km is None and time_minutes is None:
        return JsonResponse(
            {"error": "حداقل یکی از پارامترهای distance (کیلومتر) یا time (دقیقه) الزامی است"},
            status=400,
        )
    polygon = request.GET.get("polygon", "").lower() in ("1", "true", "yes")
    denoise = 0
    denoise_raw = request.GET.get("denoise", "").strip()
    if denoise_raw:
        try:
            d = float(denoise_raw)
            if 0 <= d <= 1:
                denoise = d
        except (TypeError, ValueError):
            pass
    try:
        from .neshan import fetch_isochrone
        data = fetch_isochrone(
            lat_f, lng_f,
            distance_km=distance_km,
            time_minutes=time_minutes,
            polygon=polygon,
            denoise=denoise,
        )
    except Exception:
        return JsonResponse({"error": "خطا در فراخوانی سرویس محدوده در دسترس"}, status=500)
    if data is None:
        return JsonResponse({"error": "سرویس محدوده در دسترس در دسترس نیست یا پاسخ نامعتبر"}, status=502)
    return JsonResponse(data)


# -----------------------------------------------------------------------------
# نگاشت نقطه بر نقشه (Map Matching) — نگاشت نقاط خام (مثلاً GPS) به مسیر واقعی
# مستندات: https://platform.neshan.org/docs/api/routing-category/map-matching/
# -----------------------------------------------------------------------------

def map_matching_request(request):
    """
    نگاشت مجموعه نقاط به مسیر واقعی روی نقشه.
    POST: بدنهٔ JSON { "path": "lat1,lng1|lat2,lng2|..." } — حداقل ۲ نقطه، حداکثر ۱۰۰۰.
    GET (برای تست): path=lat1,lng1|lat2,lng2|...
    پاسخ: { "snappedPoints": [...], "geometry": "encoded_polyline" } یا { "error": "..." }.
    """
    path_raw = None
    if request.method == "POST":
        if request.content_type and "application/json" in request.content_type:
            try:
                import json
                body = json.loads(request.body)
                path_raw = body.get("path") if isinstance(body, dict) else None
            except (ValueError, TypeError):
                pass
        if path_raw is None and request.POST:
            path_raw = request.POST.get("path")
    else:
        path_raw = request.GET.get("path", "").strip()
    if not path_raw:
        return JsonResponse(
            {"error": "پارامتر path الزامی است (مختصات به صورت lat,lng|lat,lng|... ، حداقل ۲ نقطه)"},
            status=400,
        )
    parts = [p.strip() for p in path_raw.split("|") if p.strip()]
    if len(parts) < 2:
        return JsonResponse({"error": "path باید حداقل ۲ نقطه داشته باشد"}, status=400)
    if len(parts) > 1000:
        return JsonResponse({"error": "حداکثر ۱۰۰۰ نقطه در path مجاز است"}, status=400)
    try:
        from .neshan import fetch_map_matching
        data = fetch_map_matching(path_raw)
    except Exception:
        return JsonResponse({"error": "خطا در فراخوانی سرویس نگاشت نقطه بر نقشه"}, status=500)
    if data is None:
        return JsonResponse(
            {"error": "سرویس نگاشت نقطه بر نقشه در دسترس نیست یا مسیری برای نقاط یافت نشد"},
            status=502,
        )
    return JsonResponse(data)


# -----------------------------------------------------------------------------
# تبدیل مختصات به آدرس (Reverse Geocode) با API نشان
# -----------------------------------------------------------------------------

@require_GET
def reverse_geocode_view(request):
    """
    پراکسی تبدیل نقطه به آدرس (Reverse Geocoding) نشان.
    مستندات: https://platform.neshan.org/docs/api/search-category/reverse-geocoding/
    GET: lat, lng (اجباری). خروجی JSON: پاسخ کامل API شامل formatted_address، route_name، neighbourhood،
    city، state، municipality_zone، in_traffic_zone، in_odd_even_zone و غیره؛ به‌همراه address و address_compact برای سازگاری.
    """
    try:
        lat = float(request.GET.get("lat", 0))
        lng = float(request.GET.get("lng", 0))
    except (TypeError, ValueError):
        return JsonResponse({"error": "پارامترهای lat و lng الزامی و باید عدد باشند", "address": None, "address_compact": None}, status=400)
    try:
        from .neshan import reverse_geocode
        data = reverse_geocode(lat, lng)
    except Exception:
        data = None
    if data is None:
        return JsonResponse({"address": None, "address_compact": None, "status": None})
    addr_str = (data.get("formatted_address") or "").strip() or None
    response = dict(data)
    response.setdefault("address", addr_str)
    response.setdefault("address_compact", addr_str)
    return JsonResponse(response)


# -----------------------------------------------------------------------------
# تبدیل آدرس به مختصات (Geocoding) با API نشان
# -----------------------------------------------------------------------------

def geocode_view(request):
    """
    پراکسی تبدیل آدرس متنی به مختصات (Geocoding) نشان.
    مستندات: https://platform.neshan.org/docs/api/search-category/geocoding/
    GET: address (اجباری)، province، city، lat، lng (مرکز جستجو)، plus (0/1)،
         sw_lat، sw_lng، ne_lat، ne_lng (extent اختیاری).
    POST: JSON با address (اجباری)، province، city، location، extent، plus.
    خروجی JSON: { "items": [ { "location": { "latitude", "longitude" }, "province", "city", "neighbourhood", "unMatchedTerm" }, ... ] }
    """
    if request.method not in ("GET", "POST"):
        return JsonResponse({"error": "Method not allowed", "items": []}, status=405)
    address = None
    province = None
    city = None
    location = None
    extent = None
    plus = False
    if request.method == "GET":
        address = (request.GET.get("address") or request.GET.get("q") or "").strip()
        province = (request.GET.get("province") or "").strip() or None
        city = (request.GET.get("city") or "").strip() or None
        try:
            lat = request.GET.get("lat")
            lng = request.GET.get("lng")
            if lat is not None and lng is not None:
                location = {"latitude": float(lat), "longitude": float(lng)}
        except (TypeError, ValueError):
            pass
        try:
            sw_lat = request.GET.get("sw_lat")
            sw_lng = request.GET.get("sw_lng")
            ne_lat = request.GET.get("ne_lat")
            ne_lng = request.GET.get("ne_lng")
            if all(x is not None for x in (sw_lat, sw_lng, ne_lat, ne_lng)):
                extent = {
                    "southWest": {"latitude": float(sw_lat), "longitude": float(sw_lng)},
                    "northEast": {"latitude": float(ne_lat), "longitude": float(ne_lng)},
                }
        except (TypeError, ValueError):
            pass
        plus = request.GET.get("plus", "").strip().lower() in ("1", "true", "yes")
    else:
        try:
            body = __import__("json").loads(request.body or "{}")
        except Exception:
            return JsonResponse({"error": "Invalid JSON", "items": []}, status=400)
        address = (body.get("address") or body.get("q") or "").strip()
        province = (body.get("province") or "").strip() or None
        city = (body.get("city") or "").strip() or None
        if body.get("location"):
            location = body["location"]
        if body.get("extent"):
            extent = body["extent"]
        plus = bool(body.get("plus"))
    if not address:
        return JsonResponse({"error": "پارامتر address (یا q) الزامی است", "items": []}, status=400)
    try:
        from .neshan import geocode
        data = geocode(address, province=province, city=city, location=location, extent=extent, plus=plus)
    except Exception:
        data = None
    if data is None:
        return JsonResponse({"items": []})
    return JsonResponse(data)


# -----------------------------------------------------------------------------
# جستجوی آدرس (نشان) — برای باکس جستجو و مسیریابی در فرانت
# -----------------------------------------------------------------------------

@require_GET
def search_places(request):
    """
    جستجو در دیتابیس team13: اول شهرهای منطبق، بعد مکان‌های آن شهرها.
    شهرها اولویت دارند؛ مکان‌ها بر اساس پربازدید (تعداد استفاده در مسیر) و امتیاز (ستاره) مرتب می‌شوند.
    GET: q (متن جستجو)، limit (اختیاری، پیش‌فرض ۲۰).
    خروجی: items با item_type="city" یا "place"؛ city اول، سپس placeها.
    """
    q = (request.GET.get("q") or request.GET.get("term") or "").strip()
    if not q:
        return JsonResponse({"count": 0, "items": []})
    limit = min(100, max(1, int(request.GET.get("limit", 30))))

    # ۱) فقط شهرهایی که نام شهر (فیلد city) شامل متن جستجو است — حروف مرتبط
    city_names = list(
        Place.objects.using(TEAM13_DB)
        .filter(city__icontains=q)
        .values_list("city", flat=True)
        .distinct()[:10]
    )
    city_names = [c for c in city_names if c and str(c).strip()]
    city_items = []
    for city_name in city_names:
        first_place = (
            Place.objects.using(TEAM13_DB)
            .filter(city=city_name)
            .order_by("-latitude")
            .first()
        )
        if first_place:
            city_items.append({
                "item_type": "city",
                "title": city_name,
                "address": "شهر " + city_name,
                "lat": first_place.latitude,
                "lng": first_place.longitude,
            })

    # ۲) مکان‌ها: شهر یا نام مکان منطبق؛ مرتب‌سازی: پربازدید (route_count) سپس امتیاز (avg_rating)
    rating_subq = (
        Comment.objects.using(TEAM13_DB)
        .filter(
            target_type=Comment.TargetType.PLACE,
            target_id=OuterRef("place_id"),
        )
        .values("target_id")
        .annotate(avg=Avg("rating"))
        .values("avg")
    )
    places_qs = (
        Place.objects.using(TEAM13_DB)
        .filter(
            Q(city__icontains=q)
            | Q(translations__name__icontains=q)
        )
        .annotate(
            routes_from_c=Count("routes_from", distinct=True),
            routes_to_c=Count("routes_to", distinct=True),
        )
        .annotate(
            route_count=F("routes_from_c") + F("routes_to_c"),
            avg_rating=Coalesce(Subquery(rating_subq), 0.0),
        )
        .prefetch_related("translations")
        .distinct()
        .order_by("-route_count", "-avg_rating")[:limit]
    )
    place_items = []
    for p in places_qs:
        trans_fa = next((t for t in p.translations.all() if t.lang == "fa"), None)
        trans_en = next((t for t in p.translations.all() if t.lang == "en"), None)
        title = (trans_fa.name if trans_fa else trans_en.name if trans_en else p.city or "").strip() or str(p.get_type_display())
        address = (p.address or p.city or "").strip() or title
        place_items.append({
            "item_type": "place",
            "place_id": str(p.place_id),
            "title": title,
            "address": address,
            "lat": p.latitude,
            "lng": p.longitude,
            "city": p.city or "",
        })

    items = city_items + place_items
    return JsonResponse({"count": len(items), "items": items})


@require_GET
def neshan_search(request):
    """
    پراکسی جستجوی مکان‌مبنا (Search API) نشان.
    مستندات: https://platform.neshan.org/docs/api/search-category/search/
    GET: q یا term (متن جستجو، اجباری)، lat, lng (نقطه مرجع برای مرتب‌سازی بر اساس فاصله)، limit (اختیاری، حداکثر ۳۰).
    خروجی JSON: { "count": N, "items": [ { "title", "address", "neighbourhood", "region", "type", "category", "location": { "x", "y" }, "lat", "lng" }, ... ] }
    """
    q = (request.GET.get("q") or request.GET.get("term") or "").strip()
    if not q:
        return JsonResponse({"count": 0, "items": []})
    try:
        lat = float(request.GET.get("lat")) if request.GET.get("lat") else None
        lng = float(request.GET.get("lng")) if request.GET.get("lng") else None
    except (TypeError, ValueError):
        lat, lng = None, None
    limit = min(50, max(1, int(request.GET.get("limit", 20))))
    try:
        from .neshan import search_response
        data = search_response(q, lat=lat, lng=lng, limit=limit)
        return JsonResponse(data)
    except Exception:
        return JsonResponse({"count": 0, "items": []})


# -----------------------------------------------------------------------------
# حالت اضطراری — مراکز امدادی نزدیک
# -----------------------------------------------------------------------------

# انواع مکان‌های امدادی برای جستجو در شعاع (امداد اضطراری)
EMERGENCY_PLACE_TYPES = [
    Place.PlaceType.HOSPITAL,
    Place.PlaceType.FIRE_STATION,
    Place.PlaceType.PHARMACY,
    Place.PlaceType.CLINIC,
]


@require_GET
def places_in_radius(request):
    """
    همهٔ مکان‌های دیتابیس در شعاع مشخص (برای جستجو در محدوده).
    مستقل از لیست بارگذاری‌شده روی نقشه؛ مستقیماً از دیتابیس واکشی می‌شود.
    GET: lat, lng (اجباری)، radius_km (پیش‌فرض ۱۰)، type (اختیاری، یکی یا چند نوع با کاما)، limit (حداکثر تعداد، پیش‌فرض ۲۰۰۰).
    خروجی JSON: { "places": [ { place_id, type, type_display, city, address, latitude, longitude, name_fa, name_en, distance_km }, ... ] }
    """
    try:
        lat = float(request.GET.get("lat") or request.GET.get("latitude"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "پارامتر lat لازم است."}, status=400)
    try:
        lon = float(request.GET.get("lon") or request.GET.get("lng") or request.GET.get("longitude"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "پارامتر lng لازم است."}, status=400)
    try:
        radius_km = float(request.GET.get("radius_km", "10"))
        if radius_km <= 0 or radius_km > 100:
            radius_km = 10.0
    except (TypeError, ValueError):
        radius_km = 10.0
    try:
        limit = min(5000, max(1, int(request.GET.get("limit", 2000))))
    except (TypeError, ValueError):
        limit = 2000

    type_param = (request.GET.get("type") or "").strip()
    filter_types = []
    if type_param:
        for t in type_param.split(","):
            t = t.strip().lower()
            if t and t in dict(Place.PlaceType.choices):
                filter_types.append(t)

    try:
        if filter_types:
            qs = Place.objects.using(TEAM13_DB).filter(type__in=filter_types).prefetch_related("translations")
        else:
            qs = Place.objects.using(TEAM13_DB).prefetch_related("translations")
        all_places = list(qs)
    except Exception:
        all_places = list(Place.objects.using(TEAM13_DB).prefetch_related("translations"))

    with_dist = []
    for p in all_places:
        try:
            d = _distance_km(lat, lon, float(p.latitude), float(p.longitude))
        except (TypeError, ValueError):
            continue
        if d > radius_km:
            continue
        trans_fa = next((t for t in p.translations.all() if t.lang == "fa"), None)
        trans_en = next((t for t in p.translations.all() if t.lang == "en"), None)
        name_fa = (trans_fa.name if trans_fa else "").strip()
        name_en = (trans_en.name if trans_en else "").strip()
        with_dist.append({
            "place_id": str(p.place_id),
            "type": p.type,
            "type_display": p.get_type_display(),
            "city": (p.city or "").strip(),
            "address": (p.address or "").strip() or (p.city or "").strip(),
            "latitude": float(p.latitude),
            "longitude": float(p.longitude),
            "name_fa": name_fa or name_en or p.get_type_display(),
            "name_en": name_en or name_fa or p.get_type_display(),
            "distance_km": round(d, 2),
        })
    with_dist.sort(key=lambda x: (x["distance_km"], x["type"]))
    places = with_dist[:limit]

    return JsonResponse({"places": places, "total": len(places), "radius_km": radius_km})


@require_GET
def emergency_nearby(request):
    """
    مراکز امدادی از دیتابیس (بیمارستان، آتش‌نشانی، داروخانه، کلینیک) در شعاع radius_km.
    به‌طور پیش‌فرض همهٔ انواع اورژانسی انتخاب‌شده و شعاع ۱۰ کیلومتر است.
    GET: lat, lon (یا lng)، radius_km (پیش‌فرض ۱۰)، limit (پیش‌فرض ۵۰).
    """
    try:
        lat = float(request.GET.get("lat") or request.GET.get("latitude") or 35.6892)
    except (TypeError, ValueError):
        lat = 35.6892
    try:
        lon = float(request.GET.get("lon") or request.GET.get("lng") or request.GET.get("longitude") or 51.3890)
    except (TypeError, ValueError):
        lon = 51.3890
    try:
        radius_km = float(request.GET.get("radius_km", "10"))
        if radius_km <= 0 or radius_km > 50:
            radius_km = 10.0
    except (TypeError, ValueError):
        radius_km = 10.0
    try:
        limit = min(100, max(1, int(request.GET.get("limit", 50))))
    except (TypeError, ValueError):
        limit = 50

    emergency_places = []
    try:
        all_emergency = list(
            Place.objects.using(TEAM13_DB)
            .filter(type__in=EMERGENCY_PLACE_TYPES)
            .prefetch_related("translations")
        )
        with_dist = []
        for p in all_emergency:
            try:
                d = _distance_km(lat, lon, float(p.latitude), float(p.longitude))
            except (TypeError, ValueError):
                continue
            if d > radius_km:
                continue
            trans_fa = next((t for t in p.translations.all() if t.lang == "fa"), None)
            trans_en = next((t for t in p.translations.all() if t.lang == "en"), None)
            name_fa = (trans_fa.name if trans_fa else "").strip()
            name_en = (trans_en.name if trans_en else "").strip()
            with_dist.append({
                "place_id": str(p.place_id),
                "type": p.type,
                "type_display": p.get_type_display(),
                "name_fa": name_fa or name_en or p.get_type_display(),
                "name_en": name_en or name_fa or p.get_type_display(),
                "address": (p.address or "").strip() or (p.city or "").strip(),
                "city": (p.city or "").strip(),
                "latitude": float(p.latitude),
                "longitude": float(p.longitude),
                "distance_km": round(d, 2),
                "eta_minutes": max(1, round(d / 0.5)),
                "source": "db",
            })
        with_dist.sort(key=lambda x: (x["distance_km"], x["type"]))
        emergency_places = with_dist[:limit]
    except Exception:
        emergency_places = []

    if _wants_json(request):
        return JsonResponse({
            "emergency_places": emergency_places,
            "lat": lat,
            "lon": lon,
            "radius_km": radius_km,
        })

    return render(request, f"{TEAM_NAME}/emergency.html", _team13_context(request, {
        "emergency_places": emergency_places,
        "lat": lat,
        "lon": lon,
        "radius_km": radius_km,
    }))
