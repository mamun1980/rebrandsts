# Generated by Django 4.2.3 on 2024-01-25 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sqs', '0003_alter_sqsterms_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setlist',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='siteenablesets',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]