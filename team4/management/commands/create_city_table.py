from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = 'Create City table manually'

    def handle(self, *args, **options):
        cursor = connections['team4'].cursor()
        
        # Create City table
        sql = """
        CREATE TABLE IF NOT EXISTS facilities_city (
            city_id INT AUTO_INCREMENT PRIMARY KEY,
            province_id INT NOT NULL,
            name_fa VARCHAR(100) NOT NULL,
            name_en VARCHAR(100) NOT NULL,
            location POINT NULL,
            created_at DATETIME(6) NOT NULL,
            updated_at DATETIME(6) NOT NULL,
            INDEX idx_city_province (province_id),
            UNIQUE KEY unique_province_name (province_id, name_en),
            FOREIGN KEY (province_id) REFERENCES facilities_province(province_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            cursor.execute(sql)
            self.stdout.write(self.style.SUCCESS('✅ جدول facilities_city ساخته شد'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'خطا: {str(e)}'))
