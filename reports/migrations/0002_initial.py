# Generated by Django 5.1.1 on 2024-11-22 14:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reports', '0001_initial'),
        ('reptrack_trace', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='main_store',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reports_for_main_store', to='reptrack_trace.mainstore'),
        ),
        migrations.AddField(
            model_name='report',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_for_product', to='reptrack_trace.product'),
        ),
    ]
