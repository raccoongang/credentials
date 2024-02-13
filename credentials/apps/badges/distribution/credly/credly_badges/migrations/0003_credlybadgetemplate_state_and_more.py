# Generated by Django 4.2.10 on 2024-02-11 16:14

from django.db import migrations, models
import django.db.models.deletion
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ("credly_badges", "0002_alter_credlyorganization_api_key_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="credlybadgetemplate",
            name="state",
            field=model_utils.fields.StatusField(
                choices=[
                    ("draft", "draft"),
                    ("active", "active"),
                    ("archived", "archived"),
                ],
                default="draft",
                help_text="Credly badge template state (auto-managed).",
                max_length=100,
                no_check_for_status=True,
            ),
        ),
        migrations.AlterField(
            model_name="credlybadgetemplate",
            name="organization",
            field=models.ForeignKey(
                help_text="Credly Organization - template owner.",
                on_delete=django.db.models.deletion.CASCADE,
                to="credly_badges.credlyorganization",
            ),
        ),
        migrations.AlterField(
            model_name="credlyorganization",
            name="api_key",
            field=models.CharField(
                help_text="Credly API shared secret for Credly Organization.",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="credlyorganization",
            name="name",
            field=models.CharField(
                blank=True,
                help_text="Verbose name for Credly Organization.",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="credlyorganization",
            name="uuid",
            field=models.UUIDField(
                help_text="Put your Credly Organization ID here.", unique=True
            ),
        ),
    ]