# Generated by Django 3.0 on 2022-06-02 04:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_globalinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactus',
            name='text',
            field=models.TextField(),
        ),
    ]