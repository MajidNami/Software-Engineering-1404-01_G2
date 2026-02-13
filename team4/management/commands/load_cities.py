from django.core.management.base import BaseCommand
from team4.models import City, Province
from team4.fields import Point
import json

class Command(BaseCommand):
    help = 'Load cities with location data'

    def handle(self, *args, **options):
        fixture_path = 'team4/fixtures/cities.json'
        
        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated_count = 0
        created_count = 0
        skipped_count = 0
        
        for item in data:
            city_id = item['city_id']
            name_fa = item['name_fa']
            name_en = item['name_en']
            
            province_data = item.get('province', {})
            p_id = province_data.get('province_id')
            
            try:
                province = Province.objects.using('team4').get(province_id=p_id)
            except Province.DoesNotExist:
                skipped_count += 1
                continue
            
            location = None
            loc_data = item.get('location', {})
            if loc_data.get('latitude') and loc_data.get('longitude'):
                location = Point(float(loc_data['longitude']), float(loc_data['latitude']))
            
            # --- FIX: Use update_or_create to handle Unique Constraints ---
            try:
                # We identify the city by its English Name and Province
                # This bypasses the Duplicate Entry error
                city, created = City.objects.using('team4').update_or_create(
                    name_en=name_en,
                    province=province,
                    defaults={
                        'city_id': city_id, # Sync the ID
                        'name_fa': name_fa,
                        'location': location,
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error with {name_en}: {e}'))
                skipped_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Complete: {created_count} created, {updated_count} updated, {skipped_count} skipped'
        ))