# Generated by Django 5.0.7 on 2024-07-29 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_useraccountdetails_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserAccountDetails',
        ),
    ]