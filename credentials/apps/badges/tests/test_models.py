import uuid

from django.contrib.sites.models import Site
from django.test import TestCase

from ..models import (
    BadgeProgress,
    BadgeRequirement, 
    BadgeTemplate,
    CredlyBadgeTemplate,
    CredlyOrganization,
    DataRule,
    Fulfillment
)


class DataRulesTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(uuid=uuid.uuid4(), api_key="test-api-key", name="test_organization")
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = CredlyBadgeTemplate.objects.create(organization=self.organization, uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)
        self.requirement = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            effect="award",
            description="Test description",
        )

    def test_multiple_data_rules_for_requirement(self):
        data_rule1 = DataRule.objects.create(
            requirement=self.requirement,
            data_path="user.pii.username",
            operator="eq",
            value="cucumber1997",
        )
        data_rule2 = DataRule.objects.create(
            requirement=self.requirement,
            data_path="user.pii.email",
            operator="eq",
            value="test@example.com",
        )

        data_rules = DataRule.objects.filter(requirement=self.requirement)

        self.assertEqual(data_rules.count(), 2)
        self.assertIn(data_rule1, data_rules)
        self.assertIn(data_rule2, data_rules)


class BadgeRequirementTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(uuid=uuid.uuid4(), api_key="test-api-key", name="test_organization")
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)
        self.credlybadge_template = CredlyBadgeTemplate.objects.create(organization=self.organization, uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)
    
    def test_multiple_requirements_for_badgetemplate(self):
        self.requirement1 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            effect="award",
            description="Test description",
        )
        self.requirement2 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            effect="revoke",
            description="Test description",
        )
        self.requirement3 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.ccx.course.passing.status.updated.v1",
            effect="award",
            description="Test description",
        )

        requirements = BadgeRequirement.objects.filter(template=self.badge_template)

        self.assertEqual(requirements.count(), 3)
        self.assertIn(self.requirement1, requirements)
        self.assertIn(self.requirement2, requirements)
        self.assertIn(self.requirement3, requirements)

    def test_multiple_requirements_for_credlybadgetemplate(self):
        self.requirement1 = BadgeRequirement.objects.create(
            template=self.credlybadge_template,
            event_type="org.openedx.learning.ccx.course.passing.status.updated.v1",
            effect="award",
            description="Test description",
        )
        self.requirement2 = BadgeRequirement.objects.create(
            template=self.credlybadge_template,
            event_type="org.openedx.learning.ccx.course.passing.status.updated.v1",
            effect="revoke",
            description="Test description",
        )
        self.requirement3 = BadgeRequirement.objects.create(
            template=self.credlybadge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            effect="award",
            description="Test description",
        )

        requirements = BadgeRequirement.objects.filter(template=self.credlybadge_template)

        self.assertEqual(requirements.count(), 3)
        self.assertIn(self.requirement1, requirements)
        self.assertIn(self.requirement2, requirements)
        self.assertIn(self.requirement3, requirements)

class BadgeTemplateUserProgressTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(uuid=uuid.uuid4(), api_key="test-api-key", name="test_organization")
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)
        self.credlybadge_template = CredlyBadgeTemplate.objects.create(organization=self.organization, uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)
        self.requirement1 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            description="Test description",
        )
        self.requirement2 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            description="Test description",
        )

    def test_user_progress_success(self):
        Fulfillment.objects.create(
            progress=BadgeProgress.objects.create(username="test_user", template=self.badge_template),
            requirement=self.requirement1,
        )
        self.assertEqual(self.badge_template.user_progress("test_user"), 0.5)
    
    def test_user_progress_no_fulfillments(self):
        Fulfillment.objects.filter(progress__template=self.badge_template).delete()
        self.assertEqual(self.badge_template.user_progress("test_user"), 0.0)
    
    def test_user_progress_no_requirements(self):
        BadgeRequirement.objects.filter(template=self.badge_template).delete()
        with self.assertRaises(ValueError):
            self.badge_template.user_progress("test_user")

    
class BadgeTemplateUserCompletionTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(uuid=uuid.uuid4(), api_key="test-api", name="test_organization")
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)
        self.credlybadge_template = CredlyBadgeTemplate.objects.create(organization=self.organization, uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)
        self.requirement1 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            description="Test description",
        )

    def test_user_completion_success(self):
        Fulfillment.objects.create(
            progress=BadgeProgress.objects.create(username="test_user", template=self.badge_template),
            requirement=self.requirement1,
        )
        self.assertTrue(self.badge_template.user_completion("test_user"))

    def test_user_completion_failure(self):
        self.assertFalse(self.badge_template.user_completion("test_usfer"))

    def test_user_completion_no_requirements(self):
        BadgeRequirement.objects.filter(template=self.badge_template).delete()
        with self.assertRaises(ValueError):
            self.badge_template.user_completion("test_user")


class BadgeTemplateRatioTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(uuid=uuid.uuid4(), api_key="test-api", name="test_organization")
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)
        self.credlybadge_template = CredlyBadgeTemplate.objects.create(organization=self.organization, uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)
        self.requirement1 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            description="Test description",
        )

    def test_ratio_success(self):
        Fulfillment.objects.create(
            progress=BadgeProgress.objects.create(username="test_user", template=self.badge_template),
            requirement=self.requirement1,
        )
        self.assertEqual(self.badge_template.ratio, 1.0)
    
    def test_ratio_no_fulfillments(self):
        self.assertEqual(self.badge_template.ratio, 0.0)

    def test_ratio_no_requirements(self):
        BadgeRequirement.objects.filter(template=self.badge_template).delete()
        with self.assertRaises(ValueError):
            self.badge_template.ratio
        