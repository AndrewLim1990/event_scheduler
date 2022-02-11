# Generated by Django 3.2.11 on 2022-02-11 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_alter_userevent_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userevent',
            name='state',
            field=models.CharField(choices=[('waiting_response', 'We are waiting for attendance from user'), ('waiting_suggestion', 'We are waiting for date suggestion from user'), ('waiting_validation', 'We are waiting for date validation from user'), ('waiting_for_others', 'We are waiting for other users to respond to suggestions'), ('is_attending', 'User is able to attend event'), ('is_not_attending', 'User has elected to not attend event'), ('no_communication', "We haven't sent any communication")], default='no_communication', max_length=256, null=True),
        ),
    ]
