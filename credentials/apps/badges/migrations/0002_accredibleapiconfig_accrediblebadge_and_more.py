# Generated by Django 4.2.17 on 2024-12-20 10:13

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('credentials', '0030_revoke_certificates_management_command'),
        ('badges', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccredibleAPIConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(blank=True, help_text='Accredible API configuration name.', max_length=255, null=True)),
                ('api_key', models.CharField(help_text='Accredible API key.', max_length=255)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AccredibleBadge',
            fields=[
                ('usercredential_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='credentials.usercredential')),
                ('state', model_utils.fields.StatusField(choices=[('created', 'created'), ('no_response', 'no_response'), ('error', 'error'), ('accepted', 'accepted'), ('expired', 'expired')], default='created', help_text='Accredible badge issuing state', max_length=100, no_check_for_status=True)),
                ('external_id', models.IntegerField(blank=True, help_text='Accredible service badge identifier', null=True, unique=True)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('credentials.usercredential',),
        ),
        migrations.AlterField(
            model_name='badgetemplate',
            name='icon',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='badge_templates/icons'),
        ),
        migrations.AlterField(
            model_name='badgetemplate',
            name='state',
            field=model_utils.fields.StatusField(choices=[('draft', 'draft'), ('active', 'active'), ('archived', 'archived')], default='draft', help_text='Credly badge template state (auto-managed).', max_length=100, no_check_for_status=True, null=True),
        ),
        migrations.CreateModel(
            name='AccredibleGroup',
            fields=[
                ('badgetemplate_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='badges.badgetemplate')),
                ('api_config', models.ForeignKey(help_text='Accredible API configuration.', on_delete=django.db.models.deletion.CASCADE, to='badges.accredibleapiconfig')),
            ],
            options={
                'abstract': False,
            },
            bases=('badges.badgetemplate',),
        ),
    ]
