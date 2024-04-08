from unittest import mock

import faker
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from credentials.apps.credentials.constants import UserCredentialStatus

from ..models import CredlyBadge, CredlyBadgeTemplate, CredlyOrganization
from ..services.issuers import CredlyBadgeTemplateIssuer


class CredlyBadgeTemplateIssuer(TestCase):
    issued_credential_type = CredlyBadgeTemplate
    issued_user_credential_type = CredlyBadge
    issuer = CredlyBadgeTemplateIssuer

    def setUp(self):
        # Create a test badge template
        fake = faker.Faker()
        credly_organization = CredlyOrganization.objects.create(
            uuid=fake.uuid4(),
            api_key=fake.uuid4(),
            name=fake.word()
        )
        self.badge_template = self.issued_credential_type.objects.create(
            origin=self.issued_credential_type.ORIGIN,
            site_id=1,
            uuid=fake.uuid4(),
            name=fake.word(),
            state='active',
            organization=credly_organization
        )

    def test_create_user_credential_with_status_awared(self):
        # Call create_user_credential with valid arguments
        with mock.patch('credentials.apps.badges.services.issuers.notify_badge_awarded') as mock_notify_badge_awarded:
            self.issuer().award(
                self.badge_template.id,
                'test_user'
            )

            mock_notify_badge_awarded.assert_called_once()

            # Check if user credential is created
            self.assertTrue(
                self.issued_user_credential_type.objects.filter(
                    username='test_user',
                    credential_content_type=ContentType.objects.get_for_model(
                        self.badge_template),
                    credential_id=self.badge_template.id,
                ).exists()
            )

    def test_create_user_credential_with_status_revoked(self):
        # Call create_user_credential with valid arguments
        with mock.patch('credentials.apps.badges.services.issuers.notify_badge_revoked') as mock_notify_badge_revoked:
            self.issuer().revoke(
                self.badge_template.id,
                'test_user'
            )

            mock_notify_badge_revoked.assert_called_once()

            # Check if user credential is created
            self.assertTrue(
                self.issued_user_credential_type.objects.filter(
                    username='test_user',
                    credential_content_type=ContentType.objects.get_for_model(
                        self.badge_template),
                    credential_id=self.badge_template.id,
                    status=UserCredentialStatus.REVOKED,
                ).exists()
            )
