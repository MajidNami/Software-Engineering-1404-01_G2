from django.core.management.base import BaseCommand
from team4.models import Village, City
from team4.fields import Point # Ensure this matches your PointField's helper
import json

class Command(BaseCommand):
    help = 'Load villages from JSON fixture'

    def handle(self, *args, **options):
        fixture_path = 'team4/fixtures/villages.json'
        
        # Clear existing data to avoid UniqueTogether errors
        self.stdout.write("Cleaning existing villages...")
        Village.objects.using('team4').all().delete()
        
        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found at {fixture_path}'))
            return

        created_count = 0
        skipped_count = 0

        for item in data:
            village_id = item['village_id']
            name_fa = item['name_fa']
            name_en = item['name_en']
            
            # Your model only links to City. 
            # We extract city_id from the nested JSON object.
            city_data = item.get('city', {})
            city_id = city_data.get('city_id')

            try:
                city = City.objects.using('team4').get(city_id=city_id)
            except City.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'⚠ Skipping {name_fa}: City {city_id} not found'
                ))
                skipped_count += 1
                continue

            # Process Location
            location_data = item.get('location', {})
            location = None
            if location_data.get('latitude') and location_data.get('longitude'):
                lat = float(location_data['latitude'])
                lng = float(location_data['longitude'])
                # Using Point class to match your PointField requirements
                location = Point(lng, lat)

            # Create the record
            # We use village_id=village_id because you have it in your JSON
            Village.objects.using('team4').create(
                village_id=village_id,
                name_fa=name_fa,
                name_en=name_en,
                city=city,
                location=location
            )
            created_count += 1

            if created_count % 500 == 0:
                self.stdout.write(f'... Created {created_count} villages')

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Done: {created_count} villages created, {skipped_count} skipped'
        ))