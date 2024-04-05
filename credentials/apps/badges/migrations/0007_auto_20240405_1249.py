# Generated by Django 3.2.20 on 2024-04-05 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0006_auto_20240403_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgerequirement',
            name='effect',
            field=models.CharField(choices=[('award', 'award')], default='award', help_text='Defines how this requirement contributes to badge earning.', max_length=32),
        ),
        migrations.CreateModel(
            name='BadgePenalty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('effect', models.CharField(choices=[('revoke', 'revoke')], default='revoke', help_text='Defines how this penalty contributes to badge regression.', max_length=32)),
                ('description', models.TextField(blank=True, help_text='Provide more details if needed.', null=True)),
                ('requirement', models.ForeignKey(help_text='Badge requirement for which this penalty is defined.', on_delete=django.db.models.deletion.CASCADE, to='badges.badgerequirement')),
            ],
        ),
        migrations.CreateModel(
            name='PenaltyDataRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_path', models.CharField(help_text='Public signal\'s data payload nested property path, e.g: "user.pii.username".', max_length=255, verbose_name='key path')),
                ('operator', models.CharField(choices=[('eq', '='), ('ne', '!=')], default='eq', help_text='Expected value comparison operator. https://docs.python.org/3/library/operator.html', max_length=32)),
                ('value', models.CharField(help_text='Expected value for the nested property, e.g: "cucumber1997".', max_length=255, verbose_name='expected value')),
                ('penalty', models.ForeignKey(help_text='Parent penalty for this data rule.', on_delete=django.db.models.deletion.CASCADE, to='badges.badgepenalty')),
            ],
            options={
                'unique_together': {('penalty', 'data_path', 'operator', 'value')},
            },
        ),
    ]
