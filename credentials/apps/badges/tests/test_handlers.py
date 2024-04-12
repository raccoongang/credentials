import uuid

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from credentials.apps.badges.models import BadgeRequirement, BadgeTemplate


class SignalHandlersTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(
            uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site, is_active=False
        )
        BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            description="Test description",
        )
        self.badge_template.is_active = True
        self.badge_template.save()

    def test_prevent_deletion_if_active(self):
        with self.assertRaises(ValidationError):
            self.badge_template.delete()