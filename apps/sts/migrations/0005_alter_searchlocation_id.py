# Generated by Django 4.2.3 on 2024-01-25 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sts', '0004_alter_device_id_alter_location_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='searchlocation',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]