# Generated by Django 4.0.3 on 2022-04-18 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0035_recentsearch_search_word'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.IntegerField(choices=[(1, 'likes'), (2, 'comment'), (3, 'follow'), (4, 'Repost'), (5, 'Liked_a_Repost'), (6, 'Commented_on_a_Repost'), (7, 'Post Notification')]),
        ),
    ]
