import uuid

from django.contrib.sites.models import Site
from django.test import TestCase

from ..models import BadgeRequirement, BadgeTemplate, CredlyBadgeTemplate, CredlyOrganization, DataRule


class DataRulesTestCase(TestCase):
    def setUp(self):
        self.organization = CredlyOrganization.objects.create(uuid=uuid.uuid4(), api_key="test-api-key", name="test_organization")
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template = CredlyBadgeTemplate.objects.create(organization=self.organization, uuid=uuid.uuid4(), name="test_template", state="draft", site=self.site)
        self.requirement = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
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
            description="Test description",
        )
        self.requirement2 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            description="Test description",
        )
        self.requirement3 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.ccx.course.passing.status.updated.v1",
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
            description="Test description",
        )
        self.requirement2 = BadgeRequirement.objects.create(
            template=self.credlybadge_template,
            event_type="org.openedx.learning.ccx.course.passing.status.updated.v1",
            description="Test description",
        )
        self.requirement3 = BadgeRequirement.objects.create(
            template=self.credlybadge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            description="Test description",
        )

        requirements = BadgeRequirement.objects.filter(template=self.credlybadge_template)

        self.assertEqual(requirements.count(), 3)
        self.assertIn(self.requirement1, requirements)
        self.assertIn(self.requirement2, requirements)
        self.assertIn(self.requirement3, requirements)
