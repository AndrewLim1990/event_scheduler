# Generated by Django 3.2.11 on 2022-02-11 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_alter_userevent_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='usereventtime',
            name='can_come',
            field=models.BooleanField(default=False),
        ),
    ]
