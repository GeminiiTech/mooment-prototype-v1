# Generated by Django 5.1.5 on 2025-02-02 19:16

import core.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(default='No description provided')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('albumId', models.CharField(max_length=6, unique=True)),
                ('event_date', models.DateField(blank=True, null=True)),
                ('visibility', models.CharField(choices=[('public', 'Public'), ('private', 'Private')], default='private', max_length=7)),
                ('album_picture', models.ImageField(blank=True, null=True, upload_to='albums-pictures/')),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='albums', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.ImageField(upload_to=core.models.upload_image_to)),
                ('file_name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('imageId', models.CharField(max_length=6, unique=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.album')),
            ],
        ),
    ]
