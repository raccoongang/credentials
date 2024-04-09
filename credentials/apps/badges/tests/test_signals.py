from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from ..models import BadgeTemplate, UserCredential
from ..signals.signals import BADGE_PROGRESS_COMPLETE


class BadgeSignalReceiverTestCase(TestCase):
    def setUp(self):
        # Create a test badge template
        self.badge_template = BadgeTemplate.objects.create(
            name='test', site_id=1)

    def test_signal_emission_and_receiver_execution(self):
        # Emit the signal
        BADGE_PROGRESS_COMPLETE.send(
            sender=self,
            username='test_user',
            badge_template_id=self.badge_template.id,
        )

        # UserCredential object
        user_credential = UserCredential.objects.filter(
            username='test_user',
            credential_content_type=ContentType.objects.get_for_model(
                self.badge_template),
            credential_id=self.badge_template.id,
        )

        # Check if user credential is created
        self.assertTrue(user_credential.exists())

        # Check if user credential status is 'awarded'
        self.assertTrue(user_credential[0].status == 'awarded')

    def test_behavior_for_nonexistent_badge_templates(self):
        # Emit the signal with a non-existent badge template ID
        BADGE_PROGRESS_COMPLETE.send(
            sender=self,
            username='test_user',
            badge_template_id=999,  # Non-existent ID
        )

        # Check that no user credential is created
        self.assertFalse(
            UserCredential.objects.filter(username='test_user').exists()
        )
