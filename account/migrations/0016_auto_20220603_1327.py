# Generated by Django 3.0 on 2022-06-03 13:27

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0015_auto_20220603_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalinfo',
            name='extra',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
    ]