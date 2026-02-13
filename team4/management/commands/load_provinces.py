from django.core.management.base import BaseCommand
from team4.models import Province
from team4.fields import Point
import json

class Command(BaseCommand):
    help = 'Load provinces with location data'

    def handle(self, *args, **options):
        fixture_path = 'team4/fixtures/province.json'
        
        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_count = 0
        created_count = 0
        
        for item in data:
            # Match the JSON keys exactly
            p_id = item['province_id']
            name_fa = item['name_fa']
            name_en = item['name_en']
            
            # Process location from the nested dictionary in your JSON
            location = None
            loc_data = item.get('location')
            if loc_data and loc_data.get('longitude') and loc_data.get('latitude'):
                lng = float(loc_data['longitude'])
                lat = float(loc_data['latitude'])
                location = Point(lng, lat)
            
            # Use update_or_create to simplify the logic
            province, created = Province.objects.using('team4').update_or_create(
                province_id=p_id,
                defaults={
                    'name_fa': name_fa,
                    'name_en': name_en,
                    'location': location,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ ایجاد: {name_fa}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ بروزرسانی: {name_fa}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ کامل شد: {created_count} ایجاد، {updated_count} بروزرسانی'
        ))