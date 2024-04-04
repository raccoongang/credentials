import uuid

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from openedx_events.learning.data import UserData, UserPersonalData

from ..models import BadgeRequirement, BadgeTemplate, CredlyOrganization, UserCredential
from ..services.requirements import discover_requirements
from ..services.user_credentials import identify_event_user


class BadgeRequirementDiscoveryTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(uuid=uuid.uuid4(), api_key="test-api-key",
                                                              name="test_organization")
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template", state="draft",
                                                           site=self.site)
        self.COURSE_PASSING_EVENT = "org.openedx.learning.course.passing.status.updated.v1"
        self.CCX_COURSE_PASSING_EVENT = "org.openedx.learning.ccx.course.passing.status.updated.v1"

    def test_discovery_eventtype_related_requirements(self):
        self.requirements = []
        self.requirements.append(
            BadgeRequirement.objects.create(template=self.badge_template, event_type=self.COURSE_PASSING_EVENT,
                                            effect="award", description="Test course passing award description"))
        self.requirements.append(
            BadgeRequirement.objects.create(template=self.badge_template, event_type=self.CCX_COURSE_PASSING_EVENT,
                                            effect="award", description="Test ccx course passing award description"))
        self.requirements.append(
            BadgeRequirement.objects.create(template=self.badge_template, event_type=self.CCX_COURSE_PASSING_EVENT,
                                            effect="revoke",
                                            description="Test ccx course passing revoke description"))
        course_passing_requirements = discover_requirements(event_type=self.COURSE_PASSING_EVENT)
        ccx_course_passing_requirements = discover_requirements(event_type=self.CCX_COURSE_PASSING_EVENT)
        self.assertEqual(course_passing_requirements.count(), 1)
        self.assertEqual(ccx_course_passing_requirements.count(), 2)
        self.assertEqual(course_passing_requirements[0].description, "Test course passing award description")
        self.assertEqual(ccx_course_passing_requirements[0].description, "Test ccx course passing award description")
        self.assertEqual(ccx_course_passing_requirements[1].description, "Test ccx course passing revoke description")


class IdentifyEventUserTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template", state="draft",
                                                           site=self.site)
        self.content_type = ContentType.objects.get_for_model(self.badge_template)
        self.user1 = UserCredential.objects.create(credential_content_type=self.content_type,
                                                   credential_id=self.badge_template.id, username="testuser1")
        self.user2 = UserCredential.objects.create(credential_content_type=self.content_type,
                                                   credential_id=self.badge_template.id, username="testuser2")
        self.user3 = UserCredential.objects.create(credential_content_type=self.content_type,
                                                   credential_id=self.badge_template.id, username="testuser3")

    def test_identify_event_user_success(self):
        pii1 = UserPersonalData(username="testuser1", email="testuser1@test.com", name="Test one")
        user_data1 = UserData(id=1, is_active=True, pii=pii1)
        username1 = identify_event_user(user_data1)
        self.assertIsNotNone(username1)
        self.assertEqual(username1, self.user1.username)
        pii2 = UserPersonalData(username="testuser2", email="testuser2@test.com", name="Test two")
        user_data2 = UserData(id=2, is_active=True, pii=pii2)
        username2 = identify_event_user(user_data2)
        self.assertIsNotNone(username2)
        self.assertEqual(username2, self.user2.username)

    def test_identify_event_user_failure(self):
        pii4 = UserPersonalData(username="testuser4", email="testuser4@test.com", name="Test four")
        user_data4 = UserData(id=4, is_active=True, pii=pii4)
        username4 = identify_event_user(user_data4)
        self.assertIsNone(username4)