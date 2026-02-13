import json
import os
from django.core.management.base import BaseCommand
from team4.models import Facility, City, Category
from team4.fields import Point 

class Command(BaseCommand):
    help = 'Load restaurants from fixtures with Smart ID & Name matching'

    def add_arguments(self, parser):
        parser.add_argument('--database', type=str, default='team4')
        # نام فایل پیش‌فرض برای رستوران‌ها
        parser.add_argument('--file', type=str, default='restaurants.json')

    def handle(self, *args, **options):
        db = options['database']
        filename = options['file']
        
        # پیدا کردن مسیر دقیق پوشه fixtures در اپلیکیشن team4
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        fixture_path = os.path.join(base_dir, 'fixtures', filename)
        
        # اگر در مسیر اصلی نبود، مسیر مستقیم تری را امتحان کن
        if not os.path.exists(fixture_path):
            fixture_path = os.path.join('team4', 'fixtures', filename)

        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.stdout.write(self.style.SUCCESS(f'📖 در حال خواندن فایل رستوران: {fixture_path}'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ فایل یافت نشد: {fixture_path}'))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # بهینه‌سازی: کش کردن دسته‌بندی‌ها
        categories = {c.category_id: c for c in Category.objects.using(db).all()}
        # پیدا کردن دسته‌بندی پیش‌فرض رستوران
        restaurant_category = Category.objects.using(db).filter(name_fa__contains='رستوران').first()

        for item in data:
            name_fa = item.get('name_fa')
            city_id = item.get('city_id')
            city_name = item.get('city_name_fa')
            cat_id = item.get('category_id')

            if not name_fa:
                continue

            # ۱. منطق هوشمند یافتن شهر (ID یا نام)
            city = None
            if city_id and city_id != 0:
                city = City.objects.using(db).filter(city_id=city_id).first()
            
            if not city and city_name:
                city = City.objects.using(db).filter(name_fa=city_name).first()
            
            if not city:
                self.stdout.write(self.style.WARNING(f'⚠ شهر برای {name_fa} یافت نشد (City Name: {city_name})'))
                skipped_count += 1
                continue

            # ۲. تطبیق دسته‌بندی
            category = categories.get(cat_id) or restaurant_category
            if not category:
                skipped_count += 1
                continue

            # ۳. ایجاد شیء Point (Longitude, Latitude)
            location = None
            loc_data = item.get('location', {})
            if loc_data.get('latitude') and loc_data.get('longitude'):
                location = Point(float(loc_data['longitude']), float(loc_data['latitude']))

            # ۴. نگاشت فیلدهای رستوران
            restaurant_fields = {
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
                'status': item.get('status', True),
                'is_24_hour': item.get('is_24_hour', False),
                'price_tier': item.get('price_tier', 'moderate'),
            }

            # ۵. عملیات Update or Create
            try:
                obj, created = Facility.objects.using(db).update_or_create(
                    name_fa=name_fa,
                    city=city,
                    defaults=restaurant_fields
                )
                
                # تنظیم امکانات (Many-to-Many)
                if 'amenities' in item and item['amenities']:
                    obj.amenities.set(item['amenities'])

                if created: created_count += 1
                else: updated_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ خطا در ذخیره {name_fa}: {e}'))
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ گزارش نهایی رستوران‌ها:'
            f'\n- جدید: {created_count}'
            f'\n- بروزرسانی: {updated_count}'
            f'\n- پرش: {skipped_count}'
        ))