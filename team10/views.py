from datetime import date

import jdatetime
from django.db.utils import OperationalError
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from core.auth import api_login_required
from .models import Trip


TEAM_NAME = "team10"

# ---- Constants
STYLES = [
    ("nature", "طبیعت"),
    ("history", "تاریخ و باستان"),
    ("culture", "فرهنگ"),
    ("food", "غذا"),
    ("festival", "جشنواره"),
    ("religious", "مذهبی"),
    ("adventure", "ماجراجویی"),
    ("shopping", "خرید"),
]

CITIES = [
    "تهران", "شیراز", "اصفهان", "مشهد", "تبریز", "یزد", "رشت", "کرمان", "اهواز",
    "کیش", "قشم", "کاشان", "همدان", "کرمانشاه", "بندرعباس", "قم", "ساری"
]


# ---- Helper functions
def _to_en_digits(s: str) -> str:
    """تبدیل اعداد فارسی/عربی به انگلیسی"""
    fa = "۰۱۲۳۴۵۶۷۸۹"
    ar = "٠١٢٣٤٥٦٧٨٩"
    out = s
    for i, ch in enumerate(fa):
        out = out.replace(ch, str(i))
    for i, ch in enumerate(ar):
        out = out.replace(ch, str(i))
    return out


def parse_jalali_date(s: str) -> date:
    """ورودی: 1404-11-20"""
    s = _to_en_digits(s.strip())
    jy, jm, jd = map(int, s.split("-"))
    return jdatetime.date(jy, jm, jd).togregorian()


def to_jalali_str(d: date | None) -> str | None:
    """تبدیل تاریخ میلادی به شمسی"""
    if not d:
        return None
    return jdatetime.date.fromgregorian(date=d).strftime("%Y-%m-%d")


def _safe_trips_queryset(request):
    """دریافت سفرهای ایمن بر اساس احراز هویت کاربر"""
    qs = Trip.objects.all().order_by("-created_at")
    if request.user.is_authenticated:
        qs = qs.filter(user_id=request.user.id).order_by("-created_at")
    return qs


def _mock_trips() -> list[dict]:
    """داده‌های نمونه برای سفرها"""
    return [
        {
            "id": 1,
            "destination_name": "شیراز",
            "origin_name": "تهران",
            "days": 4,
            "start_at_jalali": "1404-11-20",
            "budget_level": "ECONOMY",
            "total_cost": 13200000,
            "status": "draft",
            "status_fa": "پیش‌نویس",
        },
        {
            "id": 2,
            "destination_name": "اصفهان",
            "origin_name": "تهران",
            "days": 3,
            "start_at_jalali": "1404-12-02",
            "budget_level": "MODERATE",
            "total_cost": None,
            "status": "active",
            "status_fa": "فعال",
        },
    ]


def home(request):
    """صفحه اصلی - نمایش سفرها و فرم ایجاد سفر جدید"""
    error = None

    if request.method == "POST":
        destination = (request.POST.get("destination") or "").strip()
        origin = (request.POST.get("origin") or "").strip()
        days_raw = (request.POST.get("days") or "").strip()
        start_at_raw = (request.POST.get("start_at") or "").strip()
        people_raw = (request.POST.get("people") or "1").strip()
        budget_level = (request.POST.get("budget_level") or "MODERATE").strip()
        styles_selected = request.POST.getlist("styles")

        # Validate budget_level
        valid_budget_levels = ['ECONOMY', 'MODERATE', 'LUXURY']
        if budget_level not in valid_budget_levels:
            budget_level = 'MODERATE'

        # ---- Validation
        if not origin:
            error = "مبدأ را وارد کنید."
        elif not destination:
            error = "مقصد را وارد کنید."
        elif not start_at_raw:
            error = "تاریخ شروع را وارد کنید."
        else:
            try:
                days = int(_to_en_digits(days_raw))
                if days < 1:
                    raise ValueError()
            except ValueError:
                error = "مدت سفر باید یک عدد صحیح مثبت باشد."

        start_at = None
        if error is None:
            try:
                start_at = parse_jalali_date(start_at_raw)
            except Exception:
                error = "فرمت تاریخ شمسی درست نیست. نمونه صحیح: ۱۴۰۴-۱۱-۲۰"

        if error is None:
            try:
                people = int(_to_en_digits(people_raw))
                if people < 1:
                    people = 1
            except ValueError:
                people = 1

            try:
                trip = Trip.objects.create(
                    user_id=request.user.id if request.user.is_authenticated else 0,
                    destination_name=destination,
                    origin_name=origin,
                    days=days,
                    people=people,
                    budget_level=budget_level,
                    start_at=start_at,
                    styles=styles_selected,
                    status=Trip.Status.DRAFT,
                )
                return redirect("team10:trip_detail", trip_id=trip.id)
            except OperationalError:
                error = "فعلاً دیتابیس آماده نیست (migrate نشده)."

    # ---- GET: نمایش سفرهای اخیر
    try:
        qs = _safe_trips_queryset(request)
        trips_count = qs.count()
        trips_qs = qs[:6]

        trips = []
        for t in trips_qs:
            trips.append(
                {
                    "id": t.id,
                    "destination_name": t.destination_name,
                    "origin_name": t.origin_name,
                    "days": t.days,
                    "budget_level": t.budget_level,
                    "total_cost": t.total_cost,
                    "status": t.status,
                    "status_fa": t.get_status_display(),
                    "start_at_jalali": to_jalali_str(t.start_at),
                    "url_detail": reverse("team10:trip_detail", args=[t.id]),
                }
            )
    except OperationalError:
        mock = _mock_trips()
        trips_count = len(mock)
        trips = []
        for t in mock:
            t["url_detail"] = reverse("team10:trip_detail", args=[t["id"]])
            trips.append(t)

    # ---- Preset tours
    tours = [
        {
            "preset": "culture_3d",
            "title": "تور ۳ روزه فرهنگی",
            "subtitle": "مناسب فرهنگ و تاریخ",
            "tags_fa": ["فرهنگ", "تاریخ"],
        },
        {
            "preset": "nature_4d",
            "title": "تور ۴ روزه طبیعت‌گردی",
            "subtitle": "مناسب طبیعت و ماجراجویی",
            "tags_fa": ["طبیعت", "ماجراجویی"],
        },
        {
            "preset": "food_market",
            "title": "تور غذا و بازار",
            "subtitle": "مناسب غذا و خرید",
            "tags_fa": ["غذا", "خرید"],
        },
    ]

    return render(
        request,
        "team10/index.html",
        {
            "trips": trips,
            "trips_count": trips_count,
            "styles": STYLES,
            "tours": tours,
            "error": error,
            "cities": CITIES,
        },
    )


def trips_list(request):
    """نمایش لیست تمام سفرها"""
    try:
        qs = _safe_trips_queryset(request)
        return render(request, "team10/trips_list.html", {"trips": list(qs)})
    except OperationalError:
        return render(request, "team10/trips_list.html", {"trips": []})


def trip_detail(request, trip_id: int):
    """نمایش جزئیات یک سفر خاص"""
    try:
        qs = _safe_trips_queryset(request)
        trip = qs.filter(id=trip_id).first()
        if not trip:
            raise Http404()
        return render(
            request,
            "team10/trip_detail.html",
            {
                "trip": trip,
                "daily_plans": trip.daily_plans.all(),
                "hotel_schedules": trip.hotel_schedules.all(),
            },
        )
    except OperationalError:
        return render(
            request,
            "team10/trip_detail.html",
            {"trip": None, "trip_id": trip_id, "daily_plans": [], "hotel_schedules": []},
        )


def trip_cost(request, trip_id: int):
    """صفحه محاسبه هزینه سفر"""
    return render(request, "team10/trip_cost.html", {"trip_id": trip_id})


def trip_styles(request, trip_id: int):
    """صفحه انتخاب سبک سفر"""
    return render(request, "team10/trip_styles.html", {"trip_id": trip_id, "styles": STYLES})


def trip_replan(request, trip_id: int):
    """صفحه تعیین مجدد برنامه سفر"""
    return render(request, "team10/trip_replan.html", {"trip_id": trip_id})


def _validate_trip_data(destination: str, origin: str, days_raw: str, start_at_raw: str) -> tuple[dict, str | None]:
    """اعتبارسنجی داده‌های سفر و بازگشت خطا در صورت وجود"""
    error = None

    if not origin:
        error = "مبدأ را وارد کنید."
    elif not destination:
        error = "مقصد را وارد کنید."
    elif not start_at_raw:
        error = "تاریخ شروع را وارد کنید."
    else:
        try:
            days = int(_to_en_digits(days_raw))
            if days < 1:
                raise ValueError()
        except ValueError:
            error = "مدت سفر باید یک عدد صحیح مثبت باشد."

    start_at = None
    if error is None:
        try:
            start_at = parse_jalali_date(start_at_raw)
        except Exception:
            error = "فرمت تاریخ شمسی درست نیست. نمونه صحیح: ۱۴۰۴-۱۱-۲۰"

    return {"days": days if error is None else None, "start_at": start_at}, error


def _parse_trip_form_data(request):
    """استخراج داده‌های فرم ایجاد سفر از POST"""
    destination = (request.POST.get("destination") or "").strip()
    origin = (request.POST.get("origin") or "").strip()
    days_raw = (request.POST.get("days") or "").strip()
    start_at_raw = (request.POST.get("start_at") or "").strip()
    people_raw = (request.POST.get("people") or "1").strip()
    budget_level = (request.POST.get("budget_level") or "MODERATE").strip()
    styles_selected = request.POST.getlist("styles")

    valid_budget_levels = ['ECONOMY', 'MODERATE', 'LUXURY']
    if budget_level not in valid_budget_levels:
        budget_level = 'MODERATE'

    try:
        people = int(_to_en_digits(people_raw))
        if people < 1:
            people = 1
    except ValueError:
        people = 1

    return {
        "destination": destination,
        "origin": origin,
        "days_raw": days_raw,
        "start_at_raw": start_at_raw,
        "people": people,
        "budget_level": budget_level,
        "styles_selected": styles_selected,
    }

@api_login_required
def ping(request):
    return JsonResponse({"team": TEAM_NAME, "ok": True})


def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

def create_trip(request):
    return render(request, f"{TEAM_NAME}/create-trip.html")
