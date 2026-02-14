# Generated migration: add body to Comment for text comments

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("team13", "0004_add_route_contribution"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="body",
            field=models.TextField(blank=True),
        ),
    ]
