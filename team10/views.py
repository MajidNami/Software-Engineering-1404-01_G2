from datetime import date, datetime, timedelta
from functools import wraps

import jdatetime
from django.db.utils import OperationalError
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from core.auth import api_login_required
from .models import Trip, TripRequirements, PreferenceConstraint, TransferPlan
from .services import trip_planning_service


def team10_login_required(view_func):
    """Decorator that redirects to main login page if user is not authenticated."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/auth/')
        return view_func(request, *args, **kwargs)
    return _wrapped


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
                user_id = str(request.user.id) if request.user.is_authenticated else "0"
                start_datetime = datetime.combine(start_at, datetime.min.time())
                end_datetime = start_datetime + timedelta(days=days)
                
                # Create TripRequirements first
                requirements = TripRequirements.objects.create(
                    user_id=user_id,
                    start_at=start_datetime,
                    end_at=end_datetime,
                    destination_name=destination,
                    budget_level=budget_level,
                    travelers_count=people
                )
                
                # Create PreferenceConstraints for styles
                for style in styles_selected:
                    PreferenceConstraint.objects.create(
                        requirements=requirements,
                        tag=style,
                        description=style
                    )
                
                # Create Trip linked to requirements
                trip = Trip.objects.create(
                    user_id=user_id,
                    requirements=requirements,
                    destination_name=destination,
                    status='DRAFT',
                )
                return redirect("team10:trip_detail", trip_id=trip.id)
            except OperationalError:
                error = "فعلاً دیتابیس آماده نیست (migrate نشده)."

    # ---- GET: نمایش سفرهای اخیر و آمار
    try:
        qs = _safe_trips_queryset(request)
        trips_count = qs.count()
        
        # Calculate statistics
        active_trips_count = qs.filter(status__in=['DRAFT', 'IN_PROGRESS']).count()
        
        # Calculate average cost
        total_costs = []
        all_trips = list(qs)
        for t in all_trips:
            cost = t.calculate_total_cost()
            if cost and cost > 0:
                total_costs.append(float(cost))
        
        average_cost = sum(total_costs) / len(total_costs) if total_costs else 0
        
        # Get recent trips for display
        trips_qs = qs[:6]
        trips = []
        for t in trips_qs:
            req = t.requirements
            days = (req.end_at - req.start_at).days if req.end_at and req.start_at else 0
            styles = list(req.constraints.values_list('tag', flat=True))
            trips.append(
                {
                    "id": t.id,
                    "destination_name": t.destination_name or req.destination_name,
                    "origin_name": "",  # Not stored in model
                    "days": days,
                    "budget_level": req.budget_level,
                    "total_cost": t.calculate_total_cost(),
                    "status": t.status,
                    "status_fa": t.get_status_display(),
                    "start_at_jalali": to_jalali_str(req.start_at.date() if req.start_at else None),
                    "url_detail": reverse("team10:trip_detail", args=[t.id]),
                    "styles": styles,
                }
            )
    except OperationalError:
        trips_count = 0
        active_trips_count = 0
        average_cost = 0
        trips = []

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
            "active_trips_count": active_trips_count,
            "average_cost": average_cost,
            "styles": STYLES,
            "tours": tours,
            "error": error,
            "cities": CITIES,
        },
    )

@team10_login_required
def trips_list(request):
    """نمایش لیست تمام سفرها با فیلتر و مرتب‌سازی"""
    # Get filter parameters from request
    status_fa = request.GET.get('status', 'همه')
    date_from_str = request.GET.get('date_from', '').strip()
    date_to_str = request.GET.get('date_to', '').strip()
    destination = request.GET.get('destination', '').strip()
    search_query = request.GET.get('q', '').strip()
    sort_fa = request.GET.get('sort', 'جدیدترین')
    
    # Map Persian status to English
    status_map = {
        'همه': None,
        'پیشنویس': 'DRAFT',
        'فعال': 'IN_PROGRESS',
        'تایید شده': 'CONFIRMED',
        'تمام‌شده': 'EXPIRED',
        'لغو شده': 'CANCELLED',
    }
    status = status_map.get(status_fa, None)
    
    # Map Persian sort to English
    sort_map = {
        'جدیدترین': 'newest',
        'قدیمی‌ترین': 'oldest',
        'هزینه': 'cost',
    }
    sort_by = sort_map.get(sort_fa, 'newest')
    
    # Parse Jalali dates
    date_from = None
    date_to = None
    if date_from_str:
        try:
            date_from = parse_jalali_date(date_from_str)
        except Exception:
            pass
    if date_to_str:
        try:
            date_to = parse_jalali_date(date_to_str)
        except Exception:
            pass
    
    # Get user ID
    user_id = str(request.user.id) if request.user.is_authenticated else "0"
    
    try:
        # Get trips from service
        trips_data = trip_planning_service.get_user_trips(
            user_id=user_id,
            status=status,
            destination=destination if destination else None,
            date_from=date_from,
            date_to=date_to,
            search_query=search_query if search_query else None,
            sort_by=sort_by
        )
        
        # Add computed display fields
        trips = []
        for t in trips_data:
            start_date = t['start_at'].date() if hasattr(t['start_at'], 'date') else t['start_at']
            trips.append({
                'id': t['id'],
                'destination_name': t['destination_name'],
                'start_at_jalali': to_jalali_str(start_date),
                'days': t['days'],
                'budget_level': t['budget_level'],
                'total_cost': t['total_cost'],
                'status': t['status'],
                'status_fa': _get_status_fa(t['status']),
            })
    except OperationalError:
        trips = []
    
    return render(request, "team10/trips_list.html", {
        "trips": trips,
        "status": status_fa,
        "date_from": date_from_str,
        "date_to": date_to_str,
        "destination": destination,
        "q": search_query,
        "sort": sort_fa,
    })


def _get_status_fa(status: str) -> str:
    """Convert English status to Persian display name."""
    status_display = {
        'DRAFT': 'پیشنویس',
        'IN_PROGRESS': 'فعال',
        'CONFIRMED': 'تایید شده',
        'CANCELLED': 'لغو شده',
        'EXPIRED': 'تمام‌شده',
        'NEEDS_REGENERATION': 'نیاز به بازسازی',
    }
    return status_display.get(status, status)

@team10_login_required
def trip_detail(request, trip_id: int):
    """نمایش جزئیات یک سفر خاص"""
    try:
        qs = _safe_trips_queryset(request)
        trip = qs.filter(id=trip_id).first()
        if not trip:
            raise Http404()
        req = trip.requirements
        days_count = (req.end_at - req.start_at).days if req.end_at and req.start_at else 0
        
        # Group activities by day
        daily_plans = list(trip.daily_plans.all().order_by('start_at'))
        
        # Get all transfers for this trip
        try:
            transfers = {t.to_daily_plan_id: t for t in trip.transfer_plans.all()}
        except Exception:
            transfers = {}
        
        # Group plans by date
        days_grouped = {}
        trip_start_date = req.start_at.date() if req.start_at else None
        
        for plan in daily_plans:
            plan_date = plan.start_at.date()
            if plan_date not in days_grouped:
                days_grouped[plan_date] = []
            
            # Add transfer info if exists for this plan
            transfer = transfers.get(plan.id)
            plan_data = {
                'plan': plan,
                'transfer': transfer,
                'activity_type_fa': _get_activity_type_fa(plan.activity_type),
            }
            days_grouped[plan_date].append(plan_data)
        
        # Convert to ordered list of days
        sorted_dates = sorted(days_grouped.keys())
        days_list = []
        for i, d in enumerate(sorted_dates):
            day_num = (d - trip_start_date).days + 1 if trip_start_date else i + 1
            days_list.append({
                'day_number': day_num,
                'date': d,
                'date_jalali': to_jalali_str(d),
                'activities': days_grouped[d],
            })
        
        # Convert hotel dates to Jalali
        hotel_schedules = []
        for hotel in trip.hotel_schedules.all():
            hotel_schedules.append({
                'hotel_id': hotel.hotel_id,
                'rooms_count': hotel.rooms_count,
                'cost': hotel.cost,
                'start_at_jalali': to_jalali_str(hotel.start_at.date() if hotel.start_at else None),
                'end_at_jalali': to_jalali_str(hotel.end_at.date() if hotel.end_at else None),
            })
        
        # Convert trip start date to Jalali
        start_at_jalali = to_jalali_str(req.start_at.date() if req.start_at else None)
        
        return render(
            request,
            "team10/trip_detail.html",
            {
                "trip": trip,
                "days_count": days_count,
                "total_cost": trip.calculate_total_cost(),
                "days_list": days_list,
                "hotel_schedules": hotel_schedules,
                "start_at_jalali": start_at_jalali,
            },
        )
    except OperationalError:
        return render(
            request,
            "team10/trip_detail.html",
            {"trip": None, "trip_id": trip_id, "days_count": 0, "total_cost": 0, "days_list": [], "hotel_schedules": []},
        )


def _get_activity_type_fa(activity_type: str) -> str:
    """Convert English activity type to Persian."""
    types = {
        'SIGHTSEEING': 'گردشگری',
        'FOOD': 'غذا',
        'SHOPPING': 'خرید',
        'OUTDOOR': 'فضای باز',
        'CULTURE': 'فرهنگی',
        'RELAX': 'استراحت',
        'NIGHTLIFE': 'شب‌گردی',
        'TRANSPORT': 'حمل‌ونقل',
        'OTHER': 'سایر',
    }
    return types.get(activity_type, 'سایر')

@team10_login_required
def trip_cost(request, trip_id: int):
    """صفحه محاسبه هزینه سفر"""
    try:
        qs = _safe_trips_queryset(request)
        trip = qs.filter(id=trip_id).first()
        if not trip:
            raise Http404()
        
        # Calculate cost breakdown by category
        hotel_cost = sum(float(s.cost) for s in trip.hotel_schedules.all())
        
        # Get transfer costs from TransferPlan
        transfer_cost = 0
        transfer_details = []
        try:
            for transfer in trip.transfer_plans.all():
                cost = float(transfer.cost)
                transfer_cost += cost
                mode_display = {
                    'WALKING': 'پیاده‌روی',
                    'TAXI': 'تاکسی',
                    'PUBLIC_TRANSIT': 'حمل‌ونقل عمومی',
                    'DRIVING': 'خودرو شخصی',
                }.get(transfer.transport_mode, transfer.transport_mode)
                transfer_details.append({
                    'description': f'{mode_display} - {transfer.distance_km} کیلومتر ({transfer.duration_minutes} دقیقه)',
                    'cost': cost,
                })
        except Exception:
            pass  # TransferPlan table might not exist yet
        
        # Group daily plan costs by activity type
        food_cost = 0
        activity_transport_cost = 0  # Transport activity type costs (different from transfers)
        sightseeing_cost = 0
        other_cost = 0
        
        daily_plans_by_type = {}
        for plan in trip.daily_plans.all():
            cost = float(plan.cost)
            activity_type = plan.activity_type
            
            # Track individual items for details
            if activity_type not in daily_plans_by_type:
                daily_plans_by_type[activity_type] = []
            daily_plans_by_type[activity_type].append({
                'description': plan.description,
                'cost': cost,
            })
            
            if activity_type == 'FOOD':
                food_cost += cost
            elif activity_type == 'TRANSPORT':
                activity_transport_cost += cost
            elif activity_type in ('SIGHTSEEING', 'CULTURE'):
                sightseeing_cost += cost
            else:
                other_cost += cost
        
        # Combine transfer costs with activity transport costs
        total_transport_cost = transfer_cost + activity_transport_cost
        
        total_cost = hotel_cost + food_cost + total_transport_cost + sightseeing_cost + other_cost
        
        # Calculate percentages
        def calc_percent(value):
            return round((value / total_cost * 100) if total_cost > 0 else 0)
        
        cost_breakdown = [
            {'name': 'اقامت', 'cost': hotel_cost, 'percent': calc_percent(hotel_cost), 'type': 'hotel'},
            {'name': 'حمل‌ونقل', 'cost': total_transport_cost, 'percent': calc_percent(total_transport_cost), 'type': 'transport'},
            {'name': 'خوراک', 'cost': food_cost, 'percent': calc_percent(food_cost), 'type': 'food'},
            {'name': 'بازدید و فرهنگی', 'cost': sightseeing_cost, 'percent': calc_percent(sightseeing_cost), 'type': 'sightseeing'},
            {'name': 'تفریحی/سایر', 'cost': other_cost, 'percent': calc_percent(other_cost), 'type': 'other'},
        ]
        
        # Prepare details for expandable sections
        hotel_details = [
            {'description': f'هتل (شناسه: {s.hotel_id}) - {s.rooms_count} اتاق', 'cost': float(s.cost)}
            for s in trip.hotel_schedules.all()
        ]
        
        # Combine transfer details with activity transport details
        transport_details = transfer_details + daily_plans_by_type.get('TRANSPORT', [])
        food_details = daily_plans_by_type.get('FOOD', [])
        sightseeing_details = daily_plans_by_type.get('SIGHTSEEING', []) + daily_plans_by_type.get('CULTURE', [])
        other_details = []
        for t in ['SHOPPING', 'OUTDOOR', 'RELAX', 'NIGHTLIFE', 'OTHER']:
            other_details.extend(daily_plans_by_type.get(t, []))
        
        return render(
            request,
            "team10/trip_cost.html",
            {
                "trip": trip,
                "trip_id": trip_id,
                "total_cost": total_cost,
                "cost_breakdown": cost_breakdown,
                "hotel_details": hotel_details,
                "transport_details": transport_details,
                "food_details": food_details,
                "sightseeing_details": sightseeing_details,
                "other_details": other_details,
            },
        )
    except OperationalError:
        return render(
            request,
            "team10/trip_cost.html",
            {"trip": None, "trip_id": trip_id, "total_cost": 0, "cost_breakdown": []},
        )

@team10_login_required
def trip_styles(request, trip_id: int):
    """صفحه انتخاب سبک سفر"""
    return render(request, "team10/trip_styles.html", {"trip_id": trip_id, "styles": STYLES})

@team10_login_required
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

@team10_login_required
def base(request):
    return render(request, f"{TEAM_NAME}/index.html")

@team10_login_required
def create_trip(request):
    return render(request, f"{TEAM_NAME}/create_trip.html")
