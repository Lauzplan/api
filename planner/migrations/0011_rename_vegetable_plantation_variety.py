# Generated by Django 3.2.2 on 2021-09-02 08:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0010_auto_20210902_0829'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plantation',
            old_name='vegetable',
            new_name='variety',
        ),
    ]
