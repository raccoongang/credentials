# Generated by Django 3.2.18 on 2023-03-26 09:25

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('credentials', '0025_change_usercredentialdateoverride_date'),
        ('verifiable_credentials', '0008_auto_20230312_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssuanceConfiguration',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('enabled', models.BooleanField(default=False)),
                ('issuer_id', models.CharField(help_text='Issuer DID', max_length=255, primary_key=True, serialize=False)),
                ('issuer_key', models.JSONField(help_text='Issuer secret key. See: https://w3c-ccg.github.io/did-method-key/#ed25519-x25519')),
                ('issuer_name', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'ordering': ['enabled'],
            },
        ),
        migrations.AddField(
            model_name='issuanceline',
            name='status',
            field=models.CharField(blank=True, help_text="Keeps track on a corresponding user credential's status", max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='issuanceline',
            name='status_index',
            field=models.PositiveIntegerField(blank=True, help_text='Defines a position in the Status List sequence', null=True),
        ),
        migrations.AlterField(
            model_name='issuanceline',
            name='data_model_id',
            field=models.CharField(blank=True, choices=[('vc', 'Verifiable Credentials Data Model v1.1'), ('obv3', 'Open Badges Specification v3.0'), ('status-list-2021', 'Status List 2021')], help_text='Verifiable credential specification to use', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='issuanceline',
            name='user_credential',
            field=models.ForeignKey(blank=True, help_text='Related Open edX learner credential', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vc_issues', to='credentials.usercredential'),
        ),
    ]