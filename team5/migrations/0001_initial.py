from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Team5MediaRating",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.UUIDField(db_index=True)),
                ("user_email", models.EmailField(blank=True, default="", max_length=254)),
                ("media_id", models.CharField(db_index=True, max_length=128)),
                ("rate", models.FloatField()),
                ("liked", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["user_id", "liked"], name="team5_team5_user_id_2528c1_idx"),
                    models.Index(fields=["media_id"], name="team5_team5_media_i_e8b9b9_idx"),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name="team5mediarating",
            constraint=models.UniqueConstraint(
                fields=("user_id", "media_id"), name="team5_unique_user_media_rating"
            ),
        ),
    ]
