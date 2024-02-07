# Generated by Django 3.2.11 on 2024-02-05 17:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0016_alter_usereventtime_explicit_response'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserEventMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('has_seen', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField()),
                ('explicit_response', models.CharField(choices=[('outgoing', 'Message to user'), ('incoming', 'Message from user')], max_length=256, null=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_event_message', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_event_message', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]