# Generated by Django 2.0.1 on 2018-03-09 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0005_auto_20180309_1127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historyitem',
            name='vegetable',
        ),
        migrations.RemoveField(
            model_name='observation',
            name='bed',
        ),
        migrations.RemoveField(
            model_name='operation',
            name='bed',
        ),
        migrations.AddField(
            model_name='historyitem',
            name='area_concerned',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='planner.CultivatedArea'),
        ),
    ]