# Generated by Django 3.2.16 on 2023-03-05 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('verifiable_credentials', '0005_auto_20230218_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuanceline',
            name='data_model',
            field=models.CharField(blank=True, help_text='Data model lookup', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='issuanceline',
            name='expiration_date',
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
    ]
