# Generated by Django 4.2.3 on 2024-02-14 11:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0002_alter_partner_id'),
        ('sts', '0019_alter_leavebehindpopunderrules_property_type'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='duplicatepropertypartnerorder',
            unique_together={('bldsr', 'partner')},
        ),
    ]