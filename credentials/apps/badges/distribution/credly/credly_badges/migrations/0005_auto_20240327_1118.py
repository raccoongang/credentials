# Generated by Django 3.2.20 on 2024-03-27 11:18

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0001_initial'),
        ('credentials', '0026_alter_usercredential_credential_content_type'),
        ('credly_badges', '0004_credlybadge'),
    ]

    operations = [
        migrations.CreateModel(
            name='CredlyBadgeCredential',
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
        migrations.DeleteModel(
            name='CredlyBadge',
        ),
    ]
