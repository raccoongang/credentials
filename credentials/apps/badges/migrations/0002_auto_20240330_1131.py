# Generated by Django 3.2.20 on 2024-03-30 11:31

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('credentials', '0026_alter_usercredential_credential_content_type'),
        ('badges', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CredlyBadge',
            fields=[
                ('usercredential_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='credentials.usercredential')),
                ('state', model_utils.fields.StatusField(choices=[('created', 'created'), ('no_response', 'no_response'), ('error', 'error'), ('pending', 'pending'), ('accepted', 'accepted'), ('rejected', 'rejected'), ('revoked', 'revoked')], default='created', help_text='Credly badge issuing state', max_length=100, no_check_for_status=True)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
            bases=('credentials.usercredential',),
        ),
        migrations.CreateModel(
            name='CredlyOrganization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('uuid', models.UUIDField(help_text='Put your Credly Organization ID here.', unique=True)),
                ('api_key', models.CharField(help_text='Credly API shared secret for Credly Organization.', max_length=255)),
                ('name', models.CharField(blank=True, help_text='Verbose name for Credly Organization.', max_length=255, null=True)),
            ],
            options={
                'get_latest_by': 'modified',
                'abstract': False,
            },
        ),
        migrations.RenameField(
            model_name='datarule',
            old_name='path',
            new_name='data_path',
        ),
        migrations.AddField(
            model_name='badgetemplate',
            name='state',
            field=model_utils.fields.StatusField(choices=[(0, 'dummy')], default='draft', help_text='Credly badge template state (auto-managed).', max_length=100, no_check_for_status=True),
        ),
        migrations.CreateModel(
            name='CredlyBadgeTemplate',
            fields=[
                ('badgetemplate_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='badges.badgetemplate')),
                ('organization', models.ForeignKey(help_text='Credly Organization - template owner.', on_delete=django.db.models.deletion.CASCADE, to='badges.credlyorganization')),
            ],
            options={
                'abstract': False,
            },
            bases=('badges.badgetemplate',),
        ),
    ]
