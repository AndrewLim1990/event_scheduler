# Generated by Django 3.2.11 on 2024-03-03 02:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=None, max_length=512, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='EventTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_start', models.DateTimeField()),
                ('date_time_end', models.DateTimeField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_times', to='events.event')),
            ],
        ),
        migrations.CreateModel(
            name='UserEventTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=False)),
                ('has_seen', models.BooleanField(default=False)),
                ('explicit_response', models.CharField(choices=[('waiting_response', 'Has not answered for this event time'), ('can_come', 'Has explicitly said they can come to this time slot'), ('cannot_come', 'Has explicitly said they cannot come to this time slot')], default='waiting_response', max_length=256, null=True)),
                ('event_time', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_event_time', to='events.eventtime')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_event_time', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('waiting_response', 'We are waiting for attendance from user'), ('waiting_suggestion', 'We are waiting for date suggestion from user'), ('waiting_validation', 'We are waiting for date validation from user'), ('waiting_for_others', 'We are waiting for other users to respond to suggestions'), ('is_attending', 'User is able to attend event'), ('is_not_attending', 'User has elected to not attend event'), ('no_communication', "We haven't sent any communication")], default='no_communication', max_length=256, null=True)),
                ('is_required', models.BooleanField()),
                ('is_host', models.BooleanField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='events.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SuggestedDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_verified', models.BooleanField()),
                ('is_active', models.BooleanField()),
                ('input_text', models.CharField(max_length=256)),
                ('interpreted_start', models.DateTimeField()),
                ('interpreted_end', models.DateTimeField()),
                ('user_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggested_date', to='events.userevent')),
            ],
        ),
    ]
