from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("team3", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userinteraction",
            name="interaction_type",
            field=models.CharField(
                choices=[
                    ("view", "View"),
                    ("like", "Like"),
                    ("rate", "Rate"),
                    ("added_to_plan", "AddedToPlan"),
                    ("rejected", "Rejected"),
                    ("search", "Search"),
                ],
                max_length=32,
            ),
        ),
    ]
