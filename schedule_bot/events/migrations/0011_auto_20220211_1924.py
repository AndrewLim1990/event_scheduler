# Generated by Django 3.2.11 on 2022-02-11 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_usereventtime_can_come'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usereventtime',
            name='can_come',
        ),
        migrations.AddField(
            model_name='usereventtime',
            name='explicit_response',
            field=models.CharField(choices=[('waiting_response', 'Has not answered for this event time'), ('waiting_suggestion', 'Has explicitly said they cannot come to this time slot'), ('waiting_validation', 'Has explicitly said they can come to this time slot')], default='waiting_response', max_length=256, null=True),
        ),
    ]
