# Generated by Django 4.0.3 on 2022-03-26 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_delete_mainlike'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
