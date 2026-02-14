from django.db import models


class Team5City(models.Model):
    city_id = models.CharField(max_length=64, primary_key=True)
    city_name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        indexes = [models.Index(fields=["city_name"])]

    def __str__(self):
        return f"{self.city_name} ({self.city_id})"


class Team5Place(models.Model):
    place_id = models.CharField(max_length=128, primary_key=True)
    city = models.ForeignKey(Team5City, on_delete=models.CASCADE, related_name="places")
    place_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        indexes = [models.Index(fields=["city", "place_name"])]

    def __str__(self):
        return f"{self.place_name} ({self.place_id})"


class Team5Media(models.Model):
    media_id = models.CharField(max_length=128, primary_key=True)
    place = models.ForeignKey(Team5Place, on_delete=models.CASCADE, related_name="media")
    title = models.CharField(max_length=255)
    caption = models.TextField(blank=True, default="")

    class Meta:
        indexes = [models.Index(fields=["place"])]

    def __str__(self):
        return f"{self.media_id} - {self.title}"


class Team5MediaRating(models.Model):
    user_id = models.UUIDField(db_index=True)
    user_email = models.EmailField(blank=True, default="")
    media_id = models.CharField(max_length=128, db_index=True)
    rate = models.FloatField()
    liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user_id", "media_id"], name="team5_unique_user_media_rating")
        ]
        indexes = [
            models.Index(fields=["user_id", "liked"]),
            models.Index(fields=["media_id"]),
        ]

    def save(self, *args, **kwargs):
        self.liked = float(self.rate) >= 4.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_email or self.user_id} -> {self.media_id}: {self.rate}"
