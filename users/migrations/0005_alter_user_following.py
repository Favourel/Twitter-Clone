# Generated by Django 4.0.3 on 2022-03-25 17:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_follower_user_following'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='following_list', to=settings.AUTH_USER_MODEL),
        ),
    ]
