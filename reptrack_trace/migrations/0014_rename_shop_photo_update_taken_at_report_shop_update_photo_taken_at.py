# Generated by Django 5.1.4 on 2025-01-26 22:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reptrack_trace', '0013_report_shop_photo_update_taken_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='report',
            old_name='shop_photo_update_taken_at',
            new_name='shop_update_photo_taken_at',
        ),
    ]
