# Generated by Django 3.2.11 on 2024-03-03 02:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercontactinfo',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
