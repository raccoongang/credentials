# Generated by Django 3.2.18 on 2023-03-26 09:28

from django.db import migrations

from credentials.apps.verifiable_credentials.issuance.utils import create_issuers


def make_default_issuers(apps, schema_editor):
    create_issuers()

def reverse(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ("verifiable_credentials", "0009_auto_20230326_0925"),
    ]

    operations = [
        migrations.RunPython(make_default_issuers, reverse),
    ]
