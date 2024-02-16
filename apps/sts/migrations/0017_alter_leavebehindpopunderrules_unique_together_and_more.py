# Generated by Django 4.2.3 on 2024-02-13 05:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0002_alter_partner_id'),
        ('sts', '0016_alter_leavebehindpopunderrules_options'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='leavebehindpopunderrules',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='leavebehindpopunderrules',
            name='details_lb_partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='details_lb_partner', to='partners.partner', verbose_name='Details Leave Behind Partner'),
        ),
        migrations.AlterField(
            model_name='leavebehindpopunderrules',
            name='popunder_partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='popunder_partner', to='partners.partner', verbose_name='Pop Under Partner'),
        ),
        migrations.AlterField(
            model_name='leavebehindpopunderrules',
            name='property_type',
            field=models.CharField(choices=[('Rentals', 'rentals'), ('Hotels', 'hotels')], max_length=50),
        ),
        migrations.AlterField(
            model_name='leavebehindpopunderrules',
            name='tiles_lb_partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tiles_lb_partner', to='partners.partner', verbose_name='Tiles Leave Behind Partner'),
        ),
        migrations.AlterUniqueTogether(
            name='leavebehindpopunderrules',
            unique_together={('partner', 'location', 'device', 'property_type')},
        ),
    ]
