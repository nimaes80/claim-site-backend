# Generated by Django 3.0 on 2022-05-30 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_auto_20220529_2112'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemsetting',
            name='about_us',
            field=models.TextField(blank=True, null=True),
        ),
    ]
