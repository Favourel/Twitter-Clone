# Generated by Django 4.0.3 on 2022-04-14 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0034_recentsearch'),
    ]

    operations = [
        migrations.AddField(
            model_name='recentsearch',
            name='search_word',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
