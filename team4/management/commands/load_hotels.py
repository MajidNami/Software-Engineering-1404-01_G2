import json
from django.core.management.base import BaseCommand
from team4.models import Facility, City, Category
from team4.fields import Point

class Command(BaseCommand):
    help = 'Load hotels with Smart ID & Name matching to minimize skips'

    def add_arguments(self, parser):
        parser.add_argument('--database', type=str, default='team4')

    def handle(self, *args, **options):
        db = options['database']
        fixture_path = 'team4/fixtures/hotels.json'
        
        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {fixture_path}'))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # بهینه‌سازی: دریافت تمام دسته‌بندی‌ها در حافظه برای سرعت بیشتر
        categories = {c.category_id: c for c in Category.objects.using(db).all()}

        for item in data:
            name_fa = item.get('name_fa')
            city_id = item.get('city_id')
            city_name = item.get('city_name_fa') # نام شهر در JSON
            cat_id = item.get('category_id')

            if not name_fa:
                continue

            # ۱. تلاش برای یافتن شهر (اول با ID، اگر نشد با نام)
            city = None
            try:
                city = City.objects.using(db).get(city_id=city_id)
            except City.DoesNotExist:
                if city_name:
                    # تلاش ثانویه با نام فارسی شهر
                    city = City.objects.using(db).filter(name_fa=city_name).first()
            
            if not city:
                self.stdout.write(self.style.WARNING(f'⚠ شهر یافت نشد: {city_name} (ID: {city_id}) برای {name_fa}'))
                skipped_count += 1
                continue

            # ۲. بررسی دسته‌بندی
            category = categories.get(cat_id)
            if not category:
                # اگر هتل است اما ID پیدا نشد، اولین دسته‌بندی 'هتل' را پیدا کن
                category = Category.objects.using(db).filter(name_fa__contains='هتل').first()
            
            if not category:
                skipped_count += 1
                continue

            # ۳. پردازش موقعیت مکانی
            location = None
            loc_data = item.get('location', {})
            if loc_data.get('latitude') and loc_data.get('longitude'):
                location = Point(float(loc_data['longitude']), float(loc_data['latitude']))

            # ۴. داده‌های هتل
            hotel_data = {
                'name_en': item.get('name_en', ""),
                'category': category,
                'address': item.get('address', ""),
                'location': location,
                'phone': item.get('phone', ""),
                'email': item.get('email', ""),
                'website': item.get('website', ""),
                'description_fa': item.get('description_fa', ""),
                'description_en': item.get('description_en', ""),
                'avg_rating': item.get('avg_rating', 0.0),
                'review_count': item.get('review_count', 0),
                'status': True,
                'is_24_hour': item.get('is_24_hour', False),
                'price_tier': item.get('price_tier', 'unknown'),
            }

            # ۵. ذخیره در دیتابیس
            try:
                obj, created = Facility.objects.using(db).update_or_create(
                    name_fa=name_fa,
                    city=city,
                    defaults=hotel_data
                )
                if 'amenities' in item:
                    obj.amenities.set(item['amenities'])

                if created: created_count += 1
                else: updated_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ خطا در ذخیره {name_fa}: {e}'))
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ عملیات موفق: {created_count} ایجاد، {updated_count} بروزرسانی، {skipped_count} پرش'))