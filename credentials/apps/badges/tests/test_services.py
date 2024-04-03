import uuid

from django.contrib.sites.models import Site
from django.test import TestCase

from ..models import BadgeRequirement, BadgeTemplate, CredlyBadgeTemplate, CredlyOrganization

class BadgeRequirementDiscoveryTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(uuid=uuid.uuid4(), api_key="test-api-key", name="test_organization")
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)

        self.COURSE_PASSING_EVENT = "org.openedx.learning.course.passing.status.updated.v1"
        self.CCX_COURSE_PASSING_EVENT = "org.openedx.learning.ccx.course.passing.status.updated.v1"
    
    def test_discovery_eventtype_related_requirements(self):
        self.requirements = []

        self.requirements.append(BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type=self.COURSE_PASSING_EVENT,
            effect="award",
            description="Test course passing award description",
        ))
        self.requirements.append(BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type=self.CCX_COURSE_PASSING_EVENT,
            effect="award",
            description="Test ccx course passing award description",
        ))
        self.requirements.append(BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type=self.CCX_COURSE_PASSING_EVENT,
            effect="revoke",
            description="Test ccx course passing revoke description",
        ))

        course_passing_requirements = BadgeRequirement.objects.filter(event_type=self.COURSE_PASSING_EVENT)
        ccx_course_passing_requirements = BadgeRequirement.objects.filter(event_type=self.CCX_COURSE_PASSING_EVENT)

        self.assertEqual(course_passing_requirements.count(), 1)
        self.assertEqual(ccx_course_passing_requirements.count(), 2)

        self.assertEqual(course_passing_requirements[0].description, "Test course passing award description")
        self.assertEqual(ccx_course_passing_requirements[0].description, "Test ccx course passing award description")
        self.assertEqual(ccx_course_passing_requirements[1].description, "Test ccx course passing revoke description")