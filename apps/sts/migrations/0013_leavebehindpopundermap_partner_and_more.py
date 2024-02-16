# Generated by Django 4.2.3 on 2024-02-07 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0002_alter_partner_id'),
        ('sts', '0012_leavebehindpopundermap'),
    ]

    operations = [
        migrations.AddField(
            model_name='leavebehindpopundermap',
            name='partner',
            field=models.ForeignKey(default=11, on_delete=django.db.models.deletion.CASCADE, to='partners.partner'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='leavebehindpopundermap',
            unique_together={('bldsr', 'partner')},
        ),
    ]
