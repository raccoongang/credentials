from unittest import mock

import faker
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from credentials.apps.badges.models import CredlyBadge, CredlyBadgeTemplate, CredlyOrganization
from credentials.apps.badges.services.issuers import CredlyBadgeTemplateIssuer
from credentials.apps.badges.signals.signals import BADGE_PROGRESS_COMPLETE


class BadgeSignalReceiverTestCase(TestCase):
    def setUp(self):
        # Create a test badge template
        fake = faker.Faker()
        credly_organization = CredlyOrganization.objects.create(
            uuid=fake.uuid4(), api_key=fake.uuid4(), name=fake.word()
        )
        self.badge_template = CredlyBadgeTemplate.objects.create(
            name="test", site_id=1, organization=credly_organization
        )

    def test_signal_emission_and_receiver_execution(self):
        # Emit the signal
        with mock.patch("credentials.apps.badges.services.issuers.notify_badge_awarded"):
            with mock.patch.object(CredlyBadgeTemplateIssuer, 'issue_credly_badge'):
                BADGE_PROGRESS_COMPLETE.send(
                    sender=self,
                    username="test_user",
                    badge_template_id=self.badge_template.id,
                )

        # UserCredential object
        user_credential = CredlyBadge.objects.filter(
            username="test_user",
            credential_content_type=ContentType.objects.get_for_model(self.badge_template),
            credential_id=self.badge_template.id,
        )

        # Check if user credential is created
        self.assertTrue(user_credential.exists())

        # Check if user credential status is 'awarded'
        self.assertTrue(user_credential[0].status == "awarded")

    def test_behavior_for_nonexistent_badge_templates(self):
        # Emit the signal with a non-existent badge template ID
        with self.assertRaises(CredlyBadgeTemplate.DoesNotExist):
            BADGE_PROGRESS_COMPLETE.send(
                sender=self,
                username="test_user",
                badge_template_id=999,  # Non-existent ID
            )

        # Check that no user credential is created
        self.assertFalse(CredlyBadge.objects.filter(username="test_user").exists())
