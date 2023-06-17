from django.test import TestCase
from django.utils.translation import gettext as _

from credentials.apps.catalog.tests.factories import ProgramFactory
from credentials.apps.credentials.tests.factories import ProgramCertificateFactory

from ...issuance.tests.factories import IssuanceLineFactory
from ..open_badges import OpenBadges301DataModel, OpenBadgesDataModel


class OpenBadgesTestCase(TestCase):
    def test_open_badges_get_context(self):
        self.assertEqual(type(OpenBadgesDataModel.get_context()), list)

    def test_open_badges_get_types(self):
        self.assertEqual(type(OpenBadgesDataModel.get_types()), list)

    def test_open_badges_301_get_context(self):
        self.assertEqual(type(OpenBadges301DataModel.get_context()), list)


class TestOpenBadgesDataModel:
    """
    Open Badges v3.0 composition.
    """

    def test_default_name(self, db):
        """
        Predefined for Program certificate value is used as `name` property.
        """
        expected_default_name = "Program Certificate for passing a program Some Program"
        program = ProgramFactory(title="Some Program")
        issuance_line = IssuanceLineFactory(user_credential__credential__program_id=program.id)

        composed_obv3 = OpenBadgesDataModel(issuance_line).data

        assert composed_obv3["name"] == expected_default_name

    def test_overridden_name(self, db):
        """
        Program certificate title overrides `name` property.
        """
        expected_overridden_name = "Explicit Credential Title"
        program_certificate = ProgramCertificateFactory(title=expected_overridden_name)
        issuance_line = IssuanceLineFactory(user_credential__credential=program_certificate)

        composed_obv3 = OpenBadgesDataModel(issuance_line).data

        assert composed_obv3["name"] == expected_overridden_name
