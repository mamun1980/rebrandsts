# Generated by Django 4.2.3 on 2024-01-25 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sqs', '0004_alter_setlist_id_alter_siteenablesets_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setlistes',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
