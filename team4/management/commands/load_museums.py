import json
import os
from django.core.management.base import BaseCommand
from team4.models import Facility, City, Category, Amenity
from team4.fields import Point 
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Load museums with safety checks for duplicates and missing amenities'

    def add_arguments(self, parser):
        parser.add_argument('--database', type=str, default='team4')
        parser.add_argument('--file', type=str, default='museums.json')

    def handle(self, *args, **options):
        db = options['database']
        filename = options['file']
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        fixture_path = os.path.join(base_dir, 'fixtures', filename)
        
        if not os.path.exists(fixture_path):
            fixture_path = os.path.join('team4', 'fixtures', filename)

        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ File not found: {fixture_path}'))
            return

        # Pre-fetch all valid amenity IDs to avoid Foreign Key errors
        valid_amenity_ids = set(Amenity.objects.using(db).values_list('amenity_id', flat=True))
        
        try:
            museum_category = Category.objects.using(db).get(category_id=5)
        except Category.DoesNotExist:
            museum_category = Category.objects.using(db).filter(name_fa__contains='موزه').first()

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for item in data:
            name_fa = item.get('name_fa')
            city_id = item.get('city_id')
            city_name = item.get('city_name_fa')

            city = City.objects.using(db).filter(city_id=city_id).first() or \
                   City.objects.using(db).filter(name_fa=city_name).first()
            
            if not city:
                skipped_count += 1
                continue

            location = None
            loc_data = item.get('location', {})
            if loc_data.get('latitude') and loc_data.get('longitude'):
                location = Point(float(loc_data['longitude']), float(loc_data['latitude']))

            # Base fields
            museum_fields = {
                'name_en': item.get('name_en', ""),
                'category': museum_category,
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
                'is_24_hour': False,
                'price_tier': item.get('price_tier', 'moderate'),
            }

            try:
                # 1. Update or Create the Facility
                obj, created = Facility.objects.using(db).update_or_create(
                    name_fa=name_fa,
                    city=city,
                    defaults=museum_fields
                )
                
                # 2. Safety Check for Amenities (Fixes Error 1452)
                item_amenities = item.get('amenities', [])
                valid_to_set = [a for a in item_amenities if a in valid_amenity_ids]
                
                if valid_to_set:
                    obj.amenities.set(valid_to_set)

                if created: created_count += 1
                else: updated_count += 1

            except IntegrityError as e:
                # Fixes Error 1062 (Duplicate Name En + City ID)
                if "Duplicate entry" in str(e):
                    museum_fields['name_en'] += f" ({item.get('id')})"
                    obj, created = Facility.objects.using(db).update_or_create(
                        name_fa=name_fa,
                        city=city,
                        defaults=museum_fields
                    )
                    if created: created_count += 1
                    else: updated_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f'❌ Error saving {name_fa}: {e}'))
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error saving {name_fa}: {e}'))
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✅ Success: {created_count} created, {updated_count} updated, {skipped_count} skipped'))