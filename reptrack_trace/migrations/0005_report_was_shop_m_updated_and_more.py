# Generated by Django 5.1.4 on 2025-01-05 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reptrack_trace', '0004_report_delivered_to_shop_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='was_shop_m_updated',
            field=models.BooleanField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='was_shop_stores_updated',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
