import uuid

from django.contrib.sites.models import Site
from django.test import TestCase

from ..models import BadgeProgress, BadgeRequirement, BadgeTemplate, CredlyBadgeTemplate, CredlyOrganization, DataRule, Fulfillment


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


class RequirementFulfillmentResetTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template1", state="draft", site=self.site)
        self.badge_progress = BadgeProgress.objects.create(template=self.badge_template, username='test1')
        self.badge_requirement = BadgeRequirement.objects.create(template=self.badge_template, event_type="org.openedx.learning.course.passing.status.updated.v1")
        Fulfillment.objects.create(progress=self.badge_progress, requirement=self.badge_requirement)
    
    def test_fulfillment_reset_wrong_username(self):
        self.badge_requirement.reset('asd')
        fulfillment = Fulfillment.objects.filter(progress__username='test1').exists()
        self.assertTrue(fulfillment)

    def test_fulfillment_reset_success(self):
        self.badge_requirement.reset('test1')
        fulfillment = Fulfillment.objects.filter(progress__username='test1').exists()
        self.assertFalse(fulfillment)

    def test_fulfillment_full_reset_success(self):
        self.badge_progress.reset()
        fulfillment = Fulfillment.objects.filter(progress__username='test1').exists()
        self.assertFalse(fulfillment)
