# Generated by Django 4.0.3 on 2022-04-05 22:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_user_account_engaged_user_account_visit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='phone_number',
        ),
    ]
