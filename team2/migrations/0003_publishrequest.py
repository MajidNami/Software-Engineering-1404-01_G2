import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team2', '0002_add_timestamps'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublishRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requester_id', models.UUIDField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publish_requests', to='team2.article')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publish_requests', to='team2.version')),
            ],
            options={
                'unique_together': {('version', 'requester_id')},
            },
        ),
    ]
