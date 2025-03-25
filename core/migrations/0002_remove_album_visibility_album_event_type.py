# Generated by Django 5.1.5 on 2025-03-25 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='album',
            name='visibility',
        ),
        migrations.AddField(
            model_name='album',
            name='event_type',
            field=models.CharField(default='No event type provided', max_length=100),
        ),
    ]
