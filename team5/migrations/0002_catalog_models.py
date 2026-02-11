from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("team5", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Team5City",
            fields=[
                ("city_id", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("city_name", models.CharField(max_length=200)),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
            ],
            options={
                "indexes": [models.Index(fields=["city_name"], name="team5_team5c_city_na_f57158_idx")],
            },
        ),
        migrations.CreateModel(
            name="Team5Place",
            fields=[
                ("place_id", models.CharField(max_length=128, primary_key=True, serialize=False)),
                ("place_name", models.CharField(max_length=255)),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                (
                    "city",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="places",
                        to="team5.team5city",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["city", "place_name"], name="team5_team5p_city_id_4b6dfd_idx")
                ],
            },
        ),
        migrations.CreateModel(
            name="Team5Media",
            fields=[
                ("media_id", models.CharField(max_length=128, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("caption", models.TextField(blank=True, default="")),
                (
                    "place",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="media",
                        to="team5.team5place",
                    ),
                ),
            ],
            options={
                "indexes": [models.Index(fields=["place"], name="team5_team5m_place_i_ee7274_idx")],
            },
        ),
    ]
