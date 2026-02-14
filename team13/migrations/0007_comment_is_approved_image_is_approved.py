# Generated migration: تأیید ادمین برای نظر و عکس

from django.db import migrations, models


def set_existing_images_approved(apps, schema_editor):
    Image = apps.get_model("team13", "Image")
    Image.objects.using("team13").all().update(is_approved=True)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("team13", "0006_alter_place_type_alter_placecontribution_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="is_approved",
            field=models.BooleanField(db_column="is_approved", default=True),
        ),
        migrations.AddField(
            model_name="image",
            name="is_approved",
            field=models.BooleanField(db_column="is_approved", default=False),
        ),
        migrations.RunPython(set_existing_images_approved, noop),
    ]
