# Generated by Django 3.0 on 2022-06-04 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_auto_20220603_1339'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='withdraw',
            new_name='total_withdraw',
        ),
        migrations.AddField(
            model_name='user',
            name='last_withdraw',
            field=models.FloatField(default=0),
        ),
    ]
