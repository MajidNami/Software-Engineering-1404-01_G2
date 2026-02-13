import json
from django.core.management.base import BaseCommand
from team4.models import Category

class Command(BaseCommand):
    help = 'Load facility categories from JSON fixture'

    def add_arguments(self, parser):
        # Defaulting to 'team4' as per your setup
        parser.add_argument('--database', type=str, default='team4', help='The database to use')

    def handle(self, *args, **options):
        db = options['database']
        # Ensure this path matches your project structure
        fixture_path = 'team4/fixtures/categories.json'
        
        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Fixture not found at {fixture_path}'))
            return

        created_count = 0
        updated_count = 0

        for item in data:
            pk = item.get('pk')
            fields = item.get('fields', {})
            name_en = fields.get('name_en')

            # We use name_en for lookup because it is unique=True in your model.
            # This prevents IntegrityError if an ID mismatch occurs.
            try:
                category, created = Category.objects.using(db).update_or_create(
                    name_en=name_en,
                    defaults={
                        'category_id': pk,
                        'name_fa': fields.get('name_fa'),
                        'is_emergency': fields.get('is_emergency', False),
                        'marker_color': fields.get('marker_color', 'blue'),
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to load category "{name_en}": {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'✅ Category Load Complete: {created_count} created, {updated_count} updated on database "{db}"'
        ))