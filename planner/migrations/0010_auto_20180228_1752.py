# Generated by Django 2.0.1 on 2018-02-28 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0009_alerts_is_deleted'),
    ]

    operations = [
        migrations.RenameField(
            model_name='garden',
            old_name='user',
            new_name='users',
        ),
    ]
