# Generated by Django 3.2.12 on 2022-02-07 16:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0003_alter_eventtime_event'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='host_member',
        ),
        migrations.RemoveField(
            model_name='event',
            name='members',
        ),
        migrations.CreateModel(
            name='UserEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_required', models.BooleanField()),
                ('is_host', models.BooleanField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_events', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
