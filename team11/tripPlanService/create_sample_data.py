"""
Script to create sample trip data for testing
Run: python manage.py shell < create_sample_data.py
"""

from data.models import Trip, TripDay, TripItem
from datetime import date, time
from decimal import Decimal

print("🚀 Creating sample trip data...")

# Clean existing test data
Trip.objects.filter(title__contains="تست").delete()
print("✅ Cleaned old test data")

# Create a sample trip
trip = Trip.objects.create(
    title="سفر تستی به اصفهان",
    province="اصفهان",
    city="اصفهان",
    start_date=date(2026, 5, 1),
    duration_days=3,
    budget_level='MEDIUM',
    daily_available_hours=10,
    travel_style='FAMILY',
    generation_strategy='MIXED',
    status='DRAFT',
    total_estimated_cost=Decimal('5000000.00')
)
print(f"✅ Created Trip: {trip.title} (ID: {trip.trip_id})")

# Create Day 1
day1 = TripDay.objects.create(
    trip=trip,
    day_index=1,
    specific_date=date(2026, 5, 1),
    start_geo_location="اصفهان، میدان نقش جهان"
)
print(f"✅ Created Day 1 (ID: {day1.day_id})")

# Day 1 - Item 1: Visit Naqsh-e Jahan Square
item1 = TripItem.objects.create(
    day=day1,
    item_type='VISIT',
    place_ref_id='esfahan_naqsh_001',
    title='میدان نقش جهان',
    category='HISTORICAL',
    address_summary='اصفهان، میدان امام',
    lat=Decimal('32.6573'),
    lng=Decimal('51.6777'),
    wiki_summary='میدان نقش جهان یکی از بزرگترین میادین جهان و ثبت شده در یونسکو',
    start_time=time(9, 0),
    end_time=time(11, 30),
    duration_minutes=150,
    sort_order=1,
    price_tier='FREE',
    estimated_cost=Decimal('0.00'),
    is_locked=False
)
print(f"✅ Created Item 1: {item1.title}")

# Day 1 - Item 2: Visit Sheikh Lotfollah Mosque
item2 = TripItem.objects.create(
    day=day1,
    item_type='VISIT',
    place_ref_id='esfahan_lotfollah_002',
    title='مسجد شیخ لطف‌الله',
    category='RELIGIOUS',
    address_summary='اصفهان، میدان نقش جهان، ضلع شرقی',
    lat=Decimal('32.6575'),
    lng=Decimal('51.6782'),
    start_time=time(12, 0),
    end_time=time(13, 30),
    duration_minutes=90,
    sort_order=2,
    price_tier='BUDGET',
    estimated_cost=Decimal('200000.00'),
    is_locked=False
)
print(f"✅ Created Item 2: {item2.title}")

# Day 1 - Item 3: Lunch at traditional restaurant
item3 = TripItem.objects.create(
    day=day1,
    item_type='VISIT',
    place_ref_id='esfahan_restaurant_003',
    title='رستوران سنتی شهرزاد',
    category='DINING',
    address_summary='اصفهان، خیابان چهارباغ',
    start_time=time(14, 0),
    end_time=time(15, 30),
    duration_minutes=90,
    sort_order=3,
    price_tier='MODERATE',
    estimated_cost=Decimal('800000.00'),
    is_locked=False
)
print(f"✅ Created Item 3: {item3.title}")

# Create Day 2
day2 = TripDay.objects.create(
    trip=trip,
    day_index=2,
    specific_date=date(2026, 5, 2)
)
print(f"✅ Created Day 2 (ID: {day2.day_id})")

# Day 2 - Item 1: Visit Si-o-se-pol Bridge
item4 = TripItem.objects.create(
    day=day2,
    item_type='VISIT',
    place_ref_id='esfahan_siosepol_004',
    title='پل سی‌وسه‌پل',
    category='HISTORICAL',
    address_summary='اصفهان، زاینده رود',
    lat=Decimal('32.6470'),
    lng=Decimal('51.6648'),
    start_time=time(9, 0),
    end_time=time(10, 30),
    duration_minutes=90,
    sort_order=1,
    price_tier='FREE',
    estimated_cost=Decimal('0.00'),
    is_locked=False
)
print(f"✅ Created Item 4: {item4.title}")

# Day 2 - Item 2: Visit Chehel Sotoun Palace
item5 = TripItem.objects.create(
    day=day2,
    item_type='VISIT',
    place_ref_id='esfahan_chehelsotoun_005',
    title='کاخ چهلستون',
    category='HISTORICAL',
    address_summary='اصفهان، خیابان چهارباغ بالا',
    start_time=time(11, 0),
    end_time=time(13, 0),
    duration_minutes=120,
    sort_order=2,
    price_tier='BUDGET',
    estimated_cost=Decimal('300000.00'),
    is_locked=False
)
print(f"✅ Created Item 5: {item5.title}")

# Create Day 3
day3 = TripDay.objects.create(
    trip=trip,
    day_index=3,
    specific_date=date(2026, 5, 3)
)
print(f"✅ Created Day 3 (ID: {day3.day_id})")

# Day 3 - Item 1: Visit Vank Cathedral
item6 = TripItem.objects.create(
    day=day3,
    item_type='VISIT',
    place_ref_id='esfahan_vank_006',
    title='کلیسای وانک',
    category='RELIGIOUS',
    address_summary='اصفهان، جلفا',
    start_time=time(10, 0),
    end_time=time(12, 0),
    duration_minutes=120,
    sort_order=1,
    price_tier='BUDGET',
    estimated_cost=Decimal('250000.00'),
    is_locked=False
)
print(f"✅ Created Item 6: {item6.title}")

print("\n" + "="*50)
print(f"✅ Sample data created successfully!")
print(f"   Trip ID: {trip.trip_id}")
print(f"   Total Days: {trip.days.count()}")
print(f"   Total Items: {TripItem.objects.filter(day__trip=trip).count()}")
print(f"   Total Cost: {trip.total_estimated_cost:,} تومان")
print("="*50)

# Display summary
print("\n📊 Summary:")
for day in trip.days.all().order_by('day_index'):
    print(f"\n  روز {day.day_index} ({day.specific_date}):")
    for item in day.items.all().order_by('sort_order'):
        print(
            f"    - {item.start_time}-{item.end_time}: {item.title} ({item.estimated_cost:,} تومان)")

print("\n🎉 You can now test APIs with this data!")
print(f"   GET /api/trips/{trip.trip_id}/ to see the full trip")
