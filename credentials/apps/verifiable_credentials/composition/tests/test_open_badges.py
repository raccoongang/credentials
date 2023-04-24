from django.test import TestCase

from ..open_badges import OpenBadges301DataModel, OpenBadgesDataModel


class OpenBadgesTestCase(TestCase):
    def test_open_badges_get_context(self):
        self.assertEqual(type(OpenBadgesDataModel.get_context()), list)

    def test_open_badges_get_types(self):
        self.assertEqual(type(OpenBadgesDataModel.get_types()), list)

    def test_open_badges_301_get_context(self):
        self.assertEqual(type(OpenBadges301DataModel.get_context()), list)
