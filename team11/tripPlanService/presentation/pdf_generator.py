"""
PDF Generator for Trip Exports
Generates PDF files from Trip data for printing and sharing

Uses WeasyPrint for HTML to PDF conversion with full CSS and RTL support
Persian Font Support: Uses system fonts for proper Persian text rendering
"""
from io import BytesIO
from typing import Dict
import jdatetime
from datetime import datetime
from zoneinfo import ZoneInfo

from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

from data.models import Trip, DensityChoices, PlaceCategoryChoices


PERSIAN_DIGITS_MAP = str.maketrans({
    '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
    '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹',
    ',': '٬', '.': '٫'
})


def to_persian_digits(value) -> str:
    """Convert latin digits/punctuation in value to Persian digits."""
    if value is None:
        return '-'
    return str(value).translate(PERSIAN_DIGITS_MAP)


def get_category_emoji(category: str) -> str:
    """Get emoji for item category"""
    emoji_map = {
        'SIGHTSEEING': '🏛️',
        'FOOD': '🍽️',
        'STAY': '🏨',
        'TRANSPORT': '🚗',
        'SHOPPING': '🛍️',
        'ACTIVITY': '🎯',
        'OTHER': '📌'
    }
    return emoji_map.get(category, '📌')


def get_category_badge_class(category: str) -> str:
    """Get CSS class for category badge"""
    class_map = {
        'HISTORICAL': 'badge-visit',
        'NATURAL': 'badge-activity',
        'CULTURAL': 'badge-visit',
        'RECREATIONAL': 'badge-activity',
        'RELIGIOUS': 'badge-religious',
        'DINING': 'badge-food',
        'SIGHTSEEING': 'badge-visit',
        'FOOD': 'badge-food',
        'STAY': 'badge-stay',
        'ACTIVITY': 'badge-activity',
        'TRANSPORT': 'badge-transport',
        'SHOPPING': 'badge-shopping',
        'OTHER': 'badge-other'
    }
    return class_map.get(category, 'badge-other')


def format_time(time_obj) -> str:
    """Format time object to HH:MM"""
    if time_obj:
        return to_persian_digits(time_obj.strftime('%H:%M'))
    return '-'


def format_duration(minutes: int) -> str:
    """Format duration in minutes as HH:MM using Persian digits"""
    if not minutes:
        return '-'
    hours = minutes // 60
    mins = minutes % 60
    return to_persian_digits(f"{hours:02d}:{mins:02d}")


def format_cost(cost: float) -> str:
    """Format cost with thousands separator"""
    if not cost or cost == 0:
        return "۰ تومان"
    return f"{to_persian_digits(f'{int(cost):,}')} تومان"


def gregorian_to_jalali(greg_date) -> str:
    """Convert Gregorian date to Jalali (Persian) date"""
    try:
        j_date = jdatetime.date.fromgregorian(date=greg_date)
        return to_persian_digits(j_date.strftime('%Y/%m/%d'))
    except:
        return to_persian_digits(greg_date)


def get_day_name_persian(date_obj) -> str:
    """Get Persian name of the day"""
    weekday_names = [
        'دوشنبه', 'سه‌شنبه', 'چهارشنبه',
        'پنجشنبه', 'جمعه', 'شنبه', 'یکشنبه'
    ]
    return weekday_names[date_obj.weekday()]


def calculate_cost_breakdown(trip: Trip) -> Dict:
    """Calculate cost breakdown by category"""
    breakdown = {}
    total = 0

    for day in trip.days.all():
        for item in day.items.all():
            cost = float(item.estimated_cost or 0)
            category = item.category or 'OTHER'

            if category not in breakdown:
                breakdown[category] = {'amount': 0, 'count': 0}

            breakdown[category]['amount'] += cost
            breakdown[category]['count'] += 1
            total += cost

    # Add percentages
    for category in breakdown:
        if total > 0:
            breakdown[category]['percentage'] = (
                breakdown[category]['amount'] / total) * 100
        else:
            breakdown[category]['percentage'] = 0

    return {'breakdown': breakdown, 'total': total}


def generate_html_content(trip: Trip) -> str:
    """Generate HTML content for PDF"""

    # Get trip data
    days = trip.days.all().order_by('day_index')
    cost_data = calculate_cost_breakdown(trip)

    # Convert dates to Jalali
    jalali_start = gregorian_to_jalali(trip.start_date)
    jalali_end = gregorian_to_jalali(trip.end_date)

    # Get density and interests
    density_display = dict(DensityChoices.choices).get(
        trip.density, '-') if trip.density else '-'
    interests_display = '، '.join(trip.interests) if trip.interests else '-'

    # Start building HTML
    html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="fa">
<head>
    <meta charset="UTF-8">
    <title>{trip.title}</title>
    <style>
        :root {{
            --forest-green: #2E7D32;
            --persian-blue: #00695C;
            --persian-gold: #FFB300;
            --tile-cyan: #26C6DA;
            --mountain-grey: #37474F;
            --bg-light: #F1F8E9;
            --border-soft: #d8e8cf;
            --text-dark: #1A1A1A;
        }}
        @font-face {{
            font-family: 'Vazirmatn';
            src:
                local('Vazirmatn'),
                url('file:///app/fonts/Vazirmatn-Regular.ttf') format('truetype'),
                url('file:///app/presentation/fonts/Vazirmatn-Regular.ttf') format('truetype');
            font-weight: 400;
            font-style: normal;
        }}
        @font-face {{
            font-family: 'Vazirmatn';
            src:
                local('Vazirmatn Bold'),
                url('file:///app/fonts/Vazirmatn-Bold.ttf') format('truetype'),
                url('file:///app/presentation/fonts/Vazirmatn-Bold.ttf') format('truetype');
            font-weight: 700;
            font-style: normal;
        }}
        @page {{
            size: A4;
            margin: 1.5cm;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Vazirmatn', Tahoma, Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: var(--text-dark);
        }}
        .container {{
            width: 100%;
        }}
        h1 {{
            text-align: center;
            color: var(--persian-blue);
            font-size: 22pt;
            margin-bottom: 20px;
            padding: 12px 0 14px;
            border-bottom: 3px solid var(--forest-green);
            background: linear-gradient(180deg, #ffffff 0%, #f8fcf5 100%);
            border-radius: 10px;
        }}
        .metadata {{
            background: var(--bg-light);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 25px;
            border: 1px solid var(--border-soft);
            border-right: 6px solid var(--tile-cyan);
        }}
        .metadata-row {{
            display: flex;
            padding: 6px 0;
            border-bottom: 1px solid #dadce0;
        }}
        .metadata-row:last-child {{
            border-bottom: none;
        }}
        .metadata-label {{
            width: 30%;
            font-weight: bold;
            color: var(--mountain-grey);
        }}
        .metadata-value {{
            width: 70%;
            color: #000;
        }}
        .day-section {{
            margin-bottom: 25px;
            page-break-inside: avoid;
        }}
        .day-header {{
            background: linear-gradient(135deg, var(--persian-blue), var(--forest-green));
            color: white;
            padding: 10px 15px;
            font-size: 14pt;
            font-weight: bold;
            border-radius: 8px 8px 0 0;
        }}
        .items-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 0;
            font-size: 10pt;
            border-radius: 0 0 8px 8px;
            overflow: hidden;
        }}
        .items-table thead {{
            background: linear-gradient(135deg, var(--forest-green), var(--persian-blue));
            color: white;
        }}
        .items-table th {{
            padding: 8px 6px;
            text-align: center;
            font-weight: bold;
            border: 1px solid #dadce0;
        }}
        .items-table td {{
            padding: 8px 6px;
            border: 1px solid #dadce0;
        }}
        .items-table tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        .items-table .type-col {{ width: 12%; text-align: center; }}
        .items-table .title-col {{ text-align: right; }}
        .items-table .time-col {{ width: 18%; text-align: center; }}
        .items-table .duration-col {{ width: 12%; text-align: center; }}
        .items-table .cost-col {{ width: 15%; text-align: center; }}
        .cost-summary {{
            margin-top: 30px;
            page-break-inside: avoid;
        }}
        .cost-summary h2 {{
            color: var(--persian-blue);
            font-size: 16pt;
            margin-bottom: 12px;
        }}
        .cost-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 10pt;
            border-radius: 8px;
            overflow: hidden;
        }}
        .cost-table thead {{
            background: #E8F5E9;
        }}
        .cost-table th {{
            padding: 10px;
            text-align: right;
            font-weight: bold;
            border: 1px solid #dadce0;
        }}
        .cost-table td {{
            padding: 10px;
            text-align: right;
            border: 1px solid #dadce0;
        }}
        .cost-table tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        .cost-table tfoot {{
            background: var(--persian-gold);
            color: #3e2723;
            font-weight: bold;
            font-size: 11pt;
        }}
        .cost-table tfoot td {{
            border-color: var(--persian-gold);
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 1px 5px;
            border-radius: 7px;
            font-size: 8pt;
            font-weight: bold;
            border: 1px solid transparent;
            line-height: 1.35;
            text-align: center;
            white-space: nowrap;
        }}
        .badge-visit {{ background: #E0F2F1; color: #00695C; border-color: #80CBC4; }}
        .badge-food {{ background: #FFF8E1; color: #8D6E00; border-color: #FFD54F; }}
        .badge-stay {{ background: #E8F5E9; color: #2E7D32; border-color: #81C784; }}
        .badge-activity {{ background: #E1F5FE; color: #00838F; border-color: #80DEEA; }}
        .badge-religious {{ background: #F3E5F5; color: #6A1B9A; border-color: #CE93D8; }}
        .badge-transport {{ background: #ECEFF1; color: #37474F; border-color: #B0BEC5; }}
        .badge-shopping {{ background: #FFF3E0; color: #EF6C00; border-color: #FFB74D; }}
        .badge-other {{ background: #F5F5F5; color: #616161; border-color: #BDBDBD; }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #5f6368;
            font-size: 9pt;
            font-style: italic;
            padding-top: 15px;
            border-top: 1px solid #dadce0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🗺️ {trip.title}</h1>
        
        <div class="metadata">
            <div class="metadata-row">
                <div class="metadata-label">مقصد:</div>
                <div class="metadata-value">{trip.province}{f' - {trip.city}' if trip.city else ''}</div>
            </div>
            <div class="metadata-row">
                <div class="metadata-label">تاریخ شروع:</div>
                <div class="metadata-value">{jalali_start} ({to_persian_digits(trip.start_date)})</div>
            </div>
            <div class="metadata-row">
                <div class="metadata-label">تاریخ پایان:</div>
                <div class="metadata-value">{jalali_end} ({to_persian_digits(trip.end_date)})</div>
            </div>
            <div class="metadata-row">
                <div class="metadata-label">مدت سفر:</div>
                <div class="metadata-value">{to_persian_digits(trip.duration_days)} روز</div>
            </div>
            <div class="metadata-row">
                <div class="metadata-label">سطح بودجه:</div>
                <div class="metadata-value">{trip.get_budget_level_display() if trip.budget_level else '-'}</div>
            </div>
            <div class="metadata-row">
                <div class="metadata-label">تراکم برنامه:</div>
                <div class="metadata-value">{density_display}</div>
            </div>
            <div class="metadata-row">
                <div class="metadata-label">سبک سفر:</div>
                <div class="metadata-value">{trip.get_travel_style_display() if trip.travel_style else '-'}</div>
            </div>
            <div class="metadata-row">
                <div class="metadata-label">علاقه‌مندی‌ها:</div>
                <div class="metadata-value">{interests_display}</div>
            </div>
            <div class="metadata-row">
                <div class="metadata-label">هزینه تخمینی کل:</div>
                <div class="metadata-value" style="color: #00695C; font-weight: bold; font-size: 13pt;">{format_cost(cost_data['total'])}</div>
            </div>
        </div>
"""

    # Add days
    for day in days:
        jalali_date = gregorian_to_jalali(day.specific_date)
        day_name = get_day_name_persian(day.specific_date)

        html += f"""
        <div class="day-section">
            <div class="day-header">📅 روز {to_persian_digits(day.day_index)} - {day_name} {jalali_date} ({to_persian_digits(day.specific_date)})</div>
            <table class="items-table">
                <thead>
                    <tr>
                        <th class="type-col">نوع</th>
                        <th class="title-col">عنوان</th>
                        <th class="time-col">زمان</th>
                        <th class="duration-col">مدت</th>
                        <th class="cost-col">هزینه</th>
                    </tr>
                </thead>
                <tbody>
"""

        items = day.items.all().order_by('sort_order', 'start_time')
        if items.exists():
            for item in items:
                badge_class = get_category_badge_class(item.category)
                category_display = item.get_category_display()
                time_range = f"{format_time(item.start_time)} - {format_time(item.end_time)}"

                html += f"""
                    <tr>
                        <td class="type-col"><span class="badge {badge_class}">{category_display}</span></td>
                        <td class="title-col">{item.title}</td>
                        <td class="time-col">{time_range}</td>
                        <td class="duration-col">{format_duration(item.duration_minutes)}</td>
                        <td class="cost-col">{format_cost(item.estimated_cost)}</td>
                    </tr>
"""
        else:
            html += """
                    <tr>
                        <td colspan="5" style="text-align: center; padding: 15px; color: #5f6368; font-style: italic;">
                            هیچ برنامه‌ای برای این روز تعریف نشده است
                        </td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>
"""

    # Add cost breakdown
    html += """
        <div class="cost-summary">
            <h2>💰 خلاصه هزینه‌ها</h2>
            <table class="cost-table">
                <thead>
                    <tr>
                        <th>دسته‌بندی</th>
                        <th>مبلغ (تومان)</th>
                        <th>درصد</th>
                        <th>تعداد</th>
                    </tr>
                </thead>
                <tbody>
"""

    for category, data in sorted(cost_data['breakdown'].items(), key=lambda x: x[1]['amount'], reverse=True):
        emoji = get_category_emoji(category)
        category_display = dict(
            PlaceCategoryChoices.choices).get(category, category)

        html += f"""
                    <tr>
                        <td>{emoji} {category_display}</td>
                        <td>{format_cost(data['amount'])}</td>
                        <td>{to_persian_digits(f"{data['percentage']:.1f}")}٪</td>
                        <td>{to_persian_digits(data['count'])} مورد</td>
                    </tr>
"""

    total_items = sum(data['count']
                      for data in cost_data['breakdown'].values())

    html += f"""
                </tbody>
                <tfoot>
                    <tr>
                        <td>جمع کل</td>
                        <td>{format_cost(cost_data['total'])}</td>
                        <td>{to_persian_digits('100')}٪</td>
                        <td>{to_persian_digits(total_items)} مورد</td>
                    </tr>
                </tfoot>
            </table>
        </div>
"""

    # Add footer with Tehran timezone
    tehran_tz = ZoneInfo('Asia/Tehran')
    now_tehran = datetime.now(tehran_tz)
    jalali_now = jdatetime.datetime.fromgregorian(datetime=now_tehran)
    jalali_now_str = to_persian_digits(
        jalali_now.strftime('%Y/%m/%d %H:%M'))

    html += f"""
        <div class="footer">
            📄 این سند در تاریخ {jalali_now_str} توسط Trip Plan Service تولید شده است
        </div>
    </div>
</body>
</html>
"""

    return html


def generate_trip_pdf(trip: Trip) -> BytesIO:
    """
    Generate PDF from Trip data using WeasyPrint

    Args:
        trip: Trip model instance with prefetched days and items

    Returns:
        BytesIO: PDF file in memory
    """
    # Generate HTML content
    html_content = generate_html_content(trip)

    # Create font configuration for Persian fonts
    font_config = FontConfiguration()

    # Convert HTML to PDF
    buffer = BytesIO()
    HTML(string=html_content).write_pdf(buffer, font_config=font_config)

    # Reset buffer position
    buffer.seek(0)
    return buffer


def get_filename_for_trip(trip: Trip) -> str:
    """
    Generate safe filename for trip PDF

    Args:
        trip: Trip instance

    Returns:
        str: Filename like "trip_2_Isfahan_2026-05-01.pdf"
    """
    # Sanitize title (remove special chars)
    safe_title = "".join(c for c in trip.title if c.isalnum()
                         or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')[:30]  # Max 30 chars

    return f"trip_{trip.trip_id}_{safe_title}_{trip.start_date}.pdf"
