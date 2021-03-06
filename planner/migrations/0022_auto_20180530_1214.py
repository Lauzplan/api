# Generated by Django 2.0.1 on 2018-05-30 10:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0021_auto_20180530_0940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='biocideusage',
            name='garden',
        ),
        migrations.AddField(
            model_name='phytosanitaireusage',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Commentaire éventuel'),
        ),
        migrations.AlterField(
            model_name='phytosanitaireusage',
            name='crop_treated',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planner.CultivatedArea', verbose_name='Culture traitée'),
        ),
        migrations.DeleteModel(
            name='BiocideUsage',
        ),
    ]
