# Generated by Django 5.0.7 on 2024-08-14 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('carpark', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='carparkrates',
            old_name='parkcapacity',
            new_name='carparkcapacity',
        ),
        migrations.RenameField(
            model_name='carparkrates',
            old_name='ppcode',
            new_name='carparkcode',
        ),
        migrations.RenameField(
            model_name='carparkrates',
            old_name='ppname',
            new_name='carparkname',
        ),
    ]
