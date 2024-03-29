# Generated by Django 3.2.11 on 2024-02-18 21:22

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0016_alter_usereventtime_explicit_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
