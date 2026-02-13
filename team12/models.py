from django.db import models

class Place(models.Model):
    STYLE_CHOICES = [
        ('SOLO', 'Solo'), ('COUPLE', 'Couple'), ('FAMILY', 'Family'),
        ('FRIENDS', 'Friends'), ('BUSINESS', 'Business'),
    ]
    BUDGET_CHOICES = [
        ('ECONOMY', 'Economy'), ('MODERATE', 'Moderate'), ('LUXURY', 'Luxury'),
    ]
    SEASON_CHOICES = [
        ('SPRING', 'Spring'), ('SUMMER', 'Summer'), ('FALL', 'Fall'), ('WINTER', 'Winter')
    ]

    place_id = models.CharField(max_length=100, unique=True)
    place_name = models.CharField(max_length=255)
    region_id = models.CharField(max_length=100)
    region_name = models.CharField(max_length=255)
    budget_level = models.CharField(max_length=20, choices=BUDGET_CHOICES)
    travel_style = models.CharField(max_length=20, choices=STYLE_CHOICES)
    duration = models.IntegerField()
    season = models.CharField(max_length=20, choices=SEASON_CHOICES)
    image_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.place_name