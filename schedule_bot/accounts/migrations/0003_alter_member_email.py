# Generated by Django 3.2.11 on 2024-03-16 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_member_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='email',
            field=models.EmailField(default=None, max_length=254, null=True, unique=True),
        ),
    ]