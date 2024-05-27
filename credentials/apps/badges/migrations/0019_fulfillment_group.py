# Generated by Django 3.2.20 on 2024-04-29 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0018_alter_badgerequirement_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='fulfillment',
            name='group',
            field=models.CharField(blank=True, help_text='Group ID for the requirement.', max_length=255, null=True),
        ),
    ]