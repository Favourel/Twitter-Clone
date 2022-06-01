# Generated by Django 4.0.3 on 2022-04-08 16:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0032_alter_blogrepost_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='blog_images')),
                ('post', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='blog.post')),
            ],
        ),
    ]
