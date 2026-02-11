from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("team5", "0002_catalog_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="Team5RecommendationFeedback",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("user_id", models.UUIDField(db_index=True)),
                ("action", models.CharField(db_index=True, max_length=32)),
                ("liked", models.BooleanField(default=True)),
                ("shown_media_ids", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["user_id", "action", "-created_at"],
                        name="t5_fb_user_action_created_idx",
                    )
                ],
            },
        ),
    ]
