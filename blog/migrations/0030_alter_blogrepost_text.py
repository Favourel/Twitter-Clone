# Generated by Django 4.0.3 on 2022-04-08 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0029_alter_blogcomment_comment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogrepost',
            name='text',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
