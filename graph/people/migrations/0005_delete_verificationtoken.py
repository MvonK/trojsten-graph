# Generated by Django 3.0b1 on 2020-01-03 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0004_auto_20191118_1931'),
    ]

    operations = [
        migrations.DeleteModel(
            name='VerificationToken',
        ),
    ]