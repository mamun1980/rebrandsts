# Generated by Django 4.2.3 on 2024-01-25 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brands', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='brand',
            name='sort_order',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]