# Generated by Django 3.0 on 2022-05-26 11:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20220526_1015'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemsetting',
            name='claim_period',
            field=models.IntegerField(default=600),
        ),
        migrations.AlterField(
            model_name='user',
            name='claim_datetime',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
