from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from ..models import BadgeTemplate, UserCredential
from ..api import get_badge_template_by_id
from ..services.user_credentials import create_user_credential


class UserCredentialServiceTestCase(TestCase):
    def setUp(self):
        # Create a test badge template
        self.badge_template = BadgeTemplate.objects.create(
            origin='openedx', site_id=1)

    def test_create_user_credential(self):
        # Call create_user_credential with valid arguments
        create_user_credential('test_user', self.badge_template)

        # Check if user credential is created
        self.assertTrue(
            UserCredential.objects.filter(
                username='test_user',
                credential_content_type=ContentType.objects.get_for_model(
                    self.badge_template),
                credential_id=self.badge_template.id,
            ).exists()
        )

    def test_create_user_credential_invalid_username(self):
        # Call create_user_credential with non-existent username
        with self.assertRaises(ValueError):
            # Passing int as username
            create_user_credential(123, self.badge_template)

    def test_create_user_credential_invalid_template(self):
        # Call create_user_credential with non-existent badge template
        with self.assertRaises(TypeError):
            # Passing None as badge template
            create_user_credential('test_user', None)


class BadgeTemplateServiceTestCase(TestCase):
    def setUp(self):
        self.badge_template = BadgeTemplate.objects.create(origin='openedx', site_id=1)

    def test_get_badge_template_by_id(self):
        # Call get_badge_template_by_id with existing badge template ID
        badge_template = get_badge_template_by_id(self.badge_template.id)

        # Check if the returned badge template is correct
        self.assertEqual(badge_template, self.badge_template)

    def test_get_badge_template_by_id_nonexistent(self):
        # Call get_badge_template_by_id with non-existent ID
        badge_template = get_badge_template_by_id(999)  # Non-existent ID

        # Check that None is returned
        self.assertIsNone(badge_template)
