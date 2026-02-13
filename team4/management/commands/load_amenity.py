import json
from django.core.management.base import BaseCommand
from team4.models import Amenity

class Command(BaseCommand):
    help = 'Load amenities from JSON fixture'

    def add_arguments(self, parser):
        parser.add_argument('--database', type=str, default='team4', help='The database to use')

    def handle(self, *args, **options):
        db = options['database']
        # Path to your amenities JSON
        fixture_path = 'team4/fixtures/amenities.json'
        
        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Fixture not found at {fixture_path}'))
            return

        created_count = 0
        updated_count = 0

        for item in data:
            # Map the JSON structure to your model fields
            pk = item.get('pk')
            fields = item.get('fields', {})
            
            name_fa = fields.get('name_fa')
            name_en = fields.get('name_en')
            icon = fields.get('icon', '')

            # Use update_or_create to handle existing PKs gracefully
            amenity, created = Amenity.objects.using(db).update_or_create(
                amenity_id=pk,
                defaults={
                    'name_fa': name_fa,
                    'name_en': name_en,
                    'icon': icon
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'✅ Amenity Load Complete: {created_count} created, {updated_count} updated on database "{db}"'
        ))