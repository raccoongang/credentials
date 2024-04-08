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
            description="Test description",
        )

    def test_multiple_data_rules_for_requirement(self):
        data_rule1 = DataRule.objects.create(
            requirement=self.requirement,
            data_path="course_passing_status.user.pii.username",
            operator="eq",
            value="cucumber1997",
        )
        data_rule2 = DataRule.objects.create(
            requirement=self.requirement,
            data_path="course_passing_status.user.pii.email",
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

        
class RequirementFulfillmentCheckTestCase(TestCase):
    def setUp(self):
        self.site = Site.objects.create(domain="test_domain", name="test_name")
        self.badge_template1 = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template1", state="draft", site=self.site)
        self.badge_template2 = BadgeTemplate.objects.create(uuid=uuid.uuid4(), name="test_template2", state="draft", site=self.site)
        self.badge_progress = BadgeProgress.objects.create(template=self.badge_template1, username='test1')
        self.badge_requirement = BadgeRequirement.objects.create(template=self.badge_template1, event_type="org.openedx.learning.course.passing.status.updated.v1")
        self.fulfillment = Fulfillment.objects.create(progress=self.badge_progress, requirement=self.badge_requirement)
    
    def test_fulfillment_check_success(self):
        is_fulfilled = self.badge_requirement.is_fullfiled('test1')
        self.assertTrue(is_fulfilled)
    
    def test_fulfillment_check_wrong_username(self):
        is_fulfilled = self.badge_requirement.is_fullfiled('asd')
        self.assertFalse(is_fulfilled)
    
    def test_fulfillment_check_wrong_template(self):
        self.badge_progress.template = self.badge_template2
        self.badge_requirement.save()
        is_fulfilled = self.badge_requirement.is_fullfiled('test1')
        self.assertTrue(is_fulfilled)
        

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
        self.requirement3 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.ccx.course.passing.status.updated.v1",
            description="Test description",
        )

    def test_user_progress_success(self):
        Fulfillment.objects.create(
            progress=BadgeProgress.objects.create(username="test_user", template=self.badge_template),
            requirement=self.requirement1,
        )
        self.assertEqual(self.badge_template.user_progress("test_user"), 0.33)
    
    def test_user_progress_no_fulfillments(self):
        Fulfillment.objects.filter(progress__template=self.badge_template).delete()
        self.assertEqual(self.badge_template.user_progress("test_user"), 0.0)
    
    def test_user_progress_no_requirements(self):
        BadgeRequirement.objects.filter(template=self.badge_template).delete()
        self.assertEqual(self.badge_template.user_progress("test_user"), 0.0)

    
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
        self.assertEqual(self.badge_template.user_completion("test_user"), 0.0)


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
        self.requirement2 = BadgeRequirement.objects.create(
            template=self.badge_template,
            event_type="org.openedx.learning.course.passing.status.updated.v1",
            description="Test description",
        )
        self.progress = BadgeProgress.objects.create(username="test_user", template=self.badge_template)

    def test_ratio_no_fulfillments(self):
        self.assertEqual(self.progress.ratio, 0.00)

    def test_ratio_success(self):
        Fulfillment.objects.create(
            progress=self.progress,
            requirement=self.requirement1,
        )
        self.assertEqual(self.progress.ratio, 0.50)

    def test_ratio_no_requirements(self):
        BadgeRequirement.objects.filter(template=self.badge_template).delete()
        self.assertEqual(self.progress.ratio, 0.00)
