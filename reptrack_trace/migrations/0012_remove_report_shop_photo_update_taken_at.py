# Generated by Django 5.1.4 on 2025-01-26 21:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reptrack_trace', '0011_report_shop_photo_update_taken_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='shop_photo_update_taken_at',
        ),
    ]
