# Generated by Django 4.0.3 on 2022-04-29 17:47

from django.db import migrations
import djrichtextfield.models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0051_alter_post_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='content',
            field=djrichtextfield.models.RichTextField(),
        ),
    ]
