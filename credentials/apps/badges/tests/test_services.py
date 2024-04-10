import uuid

from django.contrib.sites.models import Site
from django.test import TestCase

from ..models import (
    BadgeRequirement,
    BadgePenalty,
    BadgeProgress,
    BadgeTemplate,
    CredlyOrganization,
    DataRule,
    Fulfillment,
    PenaltyDataRule,
)

from credentials.apps.badges.services.awarding import discover_requirements
from credentials.apps.badges.services.revocation import discover_penalties, process_penalties


class BadgeRequirementDiscoveryTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(
            uuid=uuid.uuid4(), api_key="test-api-key", name="test_organization"
        )
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(
            uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site
        )
        self.COURSE_PASSING_EVENT = "org.openedx.learning.course.passing.status.updated.v1"
        self.CCX_COURSE_PASSING_EVENT = "org.openedx.learning.ccx.course.passing.status.updated.v1"

    def test_discovery_eventtype_related_requirements(self):
        BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type=self.COURSE_PASSING_EVENT,
            description="Test course passing award description",
        )
        BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type=self.CCX_COURSE_PASSING_EVENT,
            description="Test ccx course passing award description",
        )
        BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type=self.CCX_COURSE_PASSING_EVENT,
            description="Test ccx course passing revoke description",
        )
        course_passing_requirements = discover_requirements(event_type=self.COURSE_PASSING_EVENT)
        ccx_course_passing_requirements = discover_requirements(event_type=self.CCX_COURSE_PASSING_EVENT)
        self.assertEqual(course_passing_requirements.count(), 1)
        self.assertEqual(ccx_course_passing_requirements.count(), 2)
        self.assertEqual(course_passing_requirements[0].description, "Test course passing award description")
        self.assertEqual(ccx_course_passing_requirements[0].description, "Test ccx course passing award description")
        self.assertEqual(ccx_course_passing_requirements[1].description, "Test ccx course passing revoke description")


class BadgePenaltyDiscoveryTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(
            uuid=uuid.uuid4(), api_key="test-api-key", name="test_organization"
        )
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(
            uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site
        )
        self.COURSE_PASSING_EVENT = "org.openedx.learning.course.passing.status.updated.v1"
        self.CCX_COURSE_PASSING_EVENT = "org.openedx.learning.ccx.course.passing.status.updated.v1"

    def test_discovery_eventtype_related_penalties(self):
        penalty1 = BadgePenalty.objects.create(template=self.badge_template, event_type=self.COURSE_PASSING_EVENT)
        penalty1.requirements.add(
            BadgeRequirement.objects.create(
                template=self.badge_template,
                event_type=self.COURSE_PASSING_EVENT,
                description="Test course passing award description",
            )
        )
        penalty2 = BadgePenalty.objects.create(template=self.badge_template, event_type=self.CCX_COURSE_PASSING_EVENT)
        penalty2.requirements.add(
            BadgeRequirement.objects.create(
                template=self.badge_template,
                event_type=self.CCX_COURSE_PASSING_EVENT,
                description="Test ccx course passing award description",
            )
        )
        penalty3 = BadgePenalty.objects.create(template=self.badge_template, event_type=self.CCX_COURSE_PASSING_EVENT)
        penalty3.requirements.add(
            BadgeRequirement.objects.create(
                template=self.badge_template,
                event_type=self.CCX_COURSE_PASSING_EVENT,
                description="Test ccx course passing revoke description",
            )
        ])
        course_passing_penalties = discover_penalties(event_type=self.COURSE_PASSING_EVENT)
        ccx_course_passing_penalties = discover_penalties(event_type=self.CCX_COURSE_PASSING_EVENT)
        self.assertEqual(course_passing_penalties.count(), 1)
        self.assertEqual(ccx_course_passing_penalties.count(), 2)
        self.assertEqual(
            course_passing_penalties[0].requirements.first().description, "Test course passing award description"
        )
        self.assertEqual(
            ccx_course_passing_penalties[0].requirements.first().description,
            "Test ccx course passing award description",
        )
        self.assertEqual(
            ccx_course_passing_penalties[1].requirements.first().description,
            "Test ccx course passing revoke description",
        )


class TestProcessPenalties(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(
            uuid=uuid.uuid4(), api_key="test-api-key", name="test_organization"
        )
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(
            uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site
        )
        self.COURSE_PASSING_EVENT = "org.openedx.learning.course.passing.status.updated.v1"
        self.CCX_COURSE_PASSING_EVENT = "org.openedx.learning.ccx.course.passing.status.updated.v1"

    def test_process_penalties_all_datarules_success(self):
        requirement1 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type=self.COURSE_PASSING_EVENT,
            description="Test course passing award description 1",
        )
        requirement2 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type=self.COURSE_PASSING_EVENT,
            description="Test course passing award description 2",
        )
        DataRule.objects.create(
            requirement=requirement1,
            data_path="course_passing_status.user.pii.username",
            operator="eq",
            value="test_username",
        )
        DataRule.objects.create(
            requirement=requirement2,
            data_path="course_passing_status.user.pii.email",
            operator="eq",
            value="test_email",
        )

        progress = BadgeProgress.objects.create(username="test_username")
        Fulfillment.objects.create(progress=progress, requirement=requirement1)
        Fulfillment.objects.create(progress=progress, requirement=requirement2)

        self.assertEqual(BadgeProgress.objects.filter(username="test_username").count(), 1)
        self.assertEqual(Fulfillment.objects.filter(progress=progress).count(), 2)
        self.assertEqual(Fulfillment.objects.filter(progress=progress, requirement=requirement1).count(), 1)
        self.assertEqual(Fulfillment.objects.filter(progress=progress, requirement=requirement1).count(), 1)

        bp = BadgePenalty.objects.create(
            template=self.badge_template, event_type=self.COURSE_PASSING_EVENT
        )
        bp.requirements.set(
            (requirement1, requirement2),
        )
        PenaltyDataRule.objects.create(
            penalty=bp,
            data_path="course_passing_status.user.pii.username",
            operator="ne",
            value="test_username1",
        )
        PenaltyDataRule.objects.create(
            penalty=bp,
            data_path="course_passing_status.user.pii.email",
            operator="ne",
            value="test_email1",
        )
        self.badge_template.is_active = True
        self.badge_template.save()
        kwargs = {
            "course_passing_status": {
                "user": {
                    "pii": {"username": "test_username", "email": "test_email", "name": "test_name"},
                }
            }
        }
        process_penalties(self.COURSE_PASSING_EVENT, "test_username", kwargs)
        self.assertEqual(Fulfillment.objects.filter(progress=progress).count(), 0)

    def test_process_penalties_one_datarule_fail(self):
        requirement1 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type=self.COURSE_PASSING_EVENT,
            description="Test course passing award description 1",
        )
        requirement2 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type=self.COURSE_PASSING_EVENT,
            description="Test course passing award description 2",
        )
        DataRule.objects.create(
            requirement=requirement1,
            data_path="course_passing_status.user.pii.username",
            operator="eq",
            value="test_username",
        )
        DataRule.objects.create(
            requirement=requirement2,
            data_path="course_passing_status.user.pii.email",
            operator="eq",
            value="test_email",
        )

        progress = BadgeProgress.objects.create(username="test_username")
        Fulfillment.objects.create(progress=progress, requirement=requirement1)
        Fulfillment.objects.create(progress=progress, requirement=requirement2)

        self.assertEqual(BadgeProgress.objects.filter(username="test_username").count(), 1)
        self.assertEqual(Fulfillment.objects.filter(progress=progress).count(), 2)
        self.assertEqual(Fulfillment.objects.filter(progress=progress, requirement=requirement1).count(), 1)
        self.assertEqual(Fulfillment.objects.filter(progress=progress, requirement=requirement1).count(), 1)

        BadgePenalty.objects.create(
            template=self.badge_template, event_type=self.COURSE_PASSING_EVENT
        ).requirements.set(
            (requirement1, requirement2),
        )
        PenaltyDataRule.objects.create(
            penalty=BadgePenalty.objects.first(),
            data_path="course_passing_status.user.pii.username",
            operator="ne",
            value="test_username",
        )
        PenaltyDataRule.objects.create(
            penalty=BadgePenalty.objects.first(),
            data_path="course_passing_status.user.pii.email",
            operator="ne",
            value="test_email",
        )
        kwargs = {
            "course_passing_status": {
                "user": {
                    "pii": {"username": "test_username", "email": "test_email", "name": "test_name"},
                }
            }
        }
        process_penalties(self.COURSE_PASSING_EVENT, "test_username", kwargs)
        self.assertEqual(Fulfillment.objects.filter(progress=progress).count(), 2)
