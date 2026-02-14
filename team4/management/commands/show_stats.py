from django.core.management.base import BaseCommand
from team4.models import Facility, City, Province, Category, Amenity, Village

class Command(BaseCommand):
    help = 'Displays a clean summary of imported data counts'

    def add_arguments(self, parser):
        parser.add_argument('--database', type=str, default='team4')

    def handle(self, *args, **options):
        db = options['database']

        self.stdout.write(self.style.MIGRATE_HEADING('\n📊 DATABASE IMPORT SUMMARY'))
        self.stdout.write('==========================================')

        # 1. Infrastructure Stats
        infra_stats = [
            ('Provinces', Province),
            ('Cities', City),
            ('Villages', Village),
            ('Categories', Category),
            ('Amenities', Amenity),
        ]

        for label, model in infra_stats:
            count = model.objects.using(db).count()
            self.stdout.write(f' {label:15} | {count:6} records')

        self.stdout.write('------------------------------------------')

        # 2. Facilities Breakdown
        all_facilities = Facility.objects.using(db).all()
        total_count = all_facilities.count()

        # Get categories that actually have facilities linked to them
        categories = Category.objects.using(db).all()
        
        for cat in categories:
            count = all_facilities.filter(category=cat).count()
            if count > 0:
                # Displays: "Museums (موزه): 45"
                self.stdout.write(f' {cat.name_en:15} | {count:6} ({cat.name_fa})')

        self.stdout.write('==========================================')
        self.stdout.write(self.style.SUCCESS(f' TOTAL FACILITIES LOADED: {total_count}\n'))