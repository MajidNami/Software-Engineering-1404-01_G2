import os
from django.core.management import BaseCommand, call_command
from team4.models import Facility

class Command(BaseCommand):
    help = 'Cleans the DB and runs all load commands, showing only final counts'

    def handle(self, *args, **options):
        db = 'team4'

        # ۱. پاکسازی Facility
        self.stdout.write(self.style.WARNING('🗑️  In progress: Clearing Facility table...'))
        Facility.objects.using(db).all().delete()
        self.stdout.write(self.style.SUCCESS('✅ Facility table cleared.'))

        # ۲. لیست دستورات بارگذاری
        commands_to_run = [
            'load_provinces',
            'load_cities',
            'load_villages',
            'load_category',
            'load_amenity',
            'load_hospitals',
            'load_hotels',
            'load_restaurants',
            'load_museums',
        ]

        self.stdout.write(self.style.MIGRATE_HEADING('\n🚀 Starting Data Import...'))

        for cmd in commands_to_run:
            try:
                # اجرای دستور بدون چاپ جزییات داخلی (Silent execution)
                call_command(cmd, database=db)
                self.stdout.write(self.style.SUCCESS(f'✔ {cmd}: Completed successfully.'))
            except Exception:
                # در صورت بروز خطا فقط نام دستور را نمایش می‌دهد
                self.stdout.write(self.style.ERROR(f'✘ {cmd}: Encountered some issues during import.'))

        # ۳. نمایش آمار نهایی
        self.stdout.write(self.style.MIGRATE_HEADING('\n📊 FINAL IMPORT SUMMARY:'))
        try:
            # فراخوانی show_stats برای نمایش تعداد دقیق رکوردهای وارد شده
            call_command('show_stats', database=db)
        except Exception:
            self.stdout.write(self.style.ERROR('Could not retrieve final stats.'))

        self.stdout.write(self.style.SUCCESS('\n✨ Full process finished.'))