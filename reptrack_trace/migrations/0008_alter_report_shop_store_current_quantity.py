# Generated by Django 5.1.4 on 2025-01-06 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reptrack_trace', '0007_rename_shop_store_update_quantity_report_shop_update_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='shop_store_current_quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
