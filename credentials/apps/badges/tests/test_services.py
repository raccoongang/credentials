import uuid

from django.contrib.sites.models import Site
from django.test import TestCase

from ..models import BadgeRequirement, BadgePenalty, BadgeTemplate, CredlyOrganization
from ..services.awarding import discover_requirements
from ..services.revocation import discover_penalties


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
        BadgeRequirement.objects.create(template=self.badge_template, event_type=self.COURSE_PASSING_EVENT,
                                        description="Test course passing award description")
        BadgeRequirement.objects.create(template=self.badge_template, event_type=self.CCX_COURSE_PASSING_EVENT,
                                        description="Test ccx course passing award description")
        BadgeRequirement.objects.create(template=self.badge_template, event_type=self.CCX_COURSE_PASSING_EVENT,
                                        description="Test ccx course passing revoke description")
        course_passing_requirements = discover_requirements(event_type=self.COURSE_PASSING_EVENT)
        ccx_course_passing_requirements = discover_requirements(event_type=self.CCX_COURSE_PASSING_EVENT)
        self.assertEqual(course_passing_requirements.count(), 1)
        self.assertEqual(ccx_course_passing_requirements.count(), 2)
        self.assertEqual(course_passing_requirements[0].description, "Test course passing award description")
        self.assertEqual(ccx_course_passing_requirements[0].description, "Test ccx course passing award description")
        self.assertEqual(ccx_course_passing_requirements[1].description, "Test ccx course passing revoke description")


class BadgePenaltyDiscoveryTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(uuid=uuid.uuid4(), api_key="test-api-key",
                                                              name="test_organization")
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template", state="draft",
                                                           site=self.site)
        self.COURSE_PASSING_EVENT = "org.openedx.learning.course.passing.status.updated.v1"
        self.CCX_COURSE_PASSING_EVENT = "org.openedx.learning.ccx.course.passing.status.updated.v1"

    def test_discovery_eventtype_related_penalties(self):
        BadgePenalty.objects.create(template=self.badge_template).requirements.set(
            BadgeRequirement.objects.create(template=self.badge_template, event_type=self.COURSE_PASSING_EVENT,
                                            description="Test course passing award description"))
        BadgePenalty.objects.create(template=self.badge_template).requirements.set(
            BadgeRequirement.objects.create(template=self.badge_template, event_type=self.CCX_COURSE_PASSING_EVENT,
                                            description="Test ccx course passing award description"))
        BadgePenalty.objects.create(template=self.badge_template).requirements.set(
            BadgeRequirement.objects.create(template=self.badge_template, event_type=self.CCX_COURSE_PASSING_EVENT,
                                            description="Test ccx course passing revoke description"))
        course_passing_penalties = discover_penalties(event_type=self.COURSE_PASSING_EVENT)
        ccx_course_passing_penalties = discover_penalties(event_type=self.CCX_COURSE_PASSING_EVENT)
        self.assertEqual(course_passing_penalties.count(), 1)
        self.assertEqual(ccx_course_passing_penalties.count(), 2)
        self.assertEqual(course_passing_penalties[0].requirements.first().description,
                         "Test course passing award description")
        self.assertEqual(ccx_course_passing_penalties[0].requirements.first().description,
                            "Test ccx course passing award description")
        self.assertEqual(ccx_course_passing_penalties[1].requirements.first().description,
                            "Test ccx course passing revoke description")
