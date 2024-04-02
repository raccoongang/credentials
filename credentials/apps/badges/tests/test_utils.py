import unittest
from datetime import datetime
from attr import asdict

from openedx_events.learning.data import UserData, UserPersonalData, CourseData, CoursePassingStatusData

from ..utils import keypath, get_user_data


class TestKeypath(unittest.TestCase):
    def test_keypath_exists(self):
        payload = {
            "course": {
                "key": "105-3332",
            }
        }
        result = keypath(payload, "course.key")
        self.assertEqual(result, "105-3332")

    def test_keypath_not_exists(self):
        payload = {
            "course": {
                "id": "105-3332",
            }
        }
        result = keypath(payload, "course.key")
        self.assertIsNone(result)

    def test_keypath_deep(self):
        payload = {"course": {"data": {"identification": {"id": 25}}}}
        result = keypath(payload, "course.data.identification.id")
        self.assertEqual(result, 25)

    def test_keypath_invalid_path(self):
        payload = {
            "course": {
                "key": "105-3332",
            }
        }
        result = keypath(payload, "course.id")
        self.assertIsNone(result)


class TestGetUserData(unittest.TestCase):
    def setUp(self):
        # Set up some sample data
        # Assuming you have instantiated CourseData and UserData objects appropriately
        self.course_data_1 = CourseData(course_key="CS101", display_name="Introduction to Computer Science", start=datetime(2024, 4, 1), end=datetime(2024, 6, 1))
        self.user_data_1 = UserData(id=1, is_active=True, pii=UserPersonalData(username="user1", email="user1@example.com", name="John Doe"))

        self.course_data_2 = CourseData(course_key="PHY101", display_name="Introduction to Physics", start=datetime(2024, 4, 15), end=datetime(2024, 7, 15))
        self.user_data_2 = UserData(id=2, is_active=False, pii=UserPersonalData(username="user2", email="user2@example.com", name="Jane Doe"))

        # Generating CoursePassingStatusData instances
        self.passing_status_1 = CoursePassingStatusData(status=CoursePassingStatusData.PASSING, course=self.course_data_1, user=self.user_data_1)
        self.failing_status_1 = CoursePassingStatusData(status=CoursePassingStatusData.FAILING, course=self.course_data_2, user=self.user_data_2)


    def test_get_user_data_from_course_enrollment(self):
        # Test extracting UserData from CourseEnrollmentData
        result_1 = get_user_data(self.passing_status_1)
        self.assertIsNotNone(result_1)
        self.assertEqual(result_1.id, 1)
        self.assertTrue(result_1.is_active)
        self.assertEqual(result_1.pii.username, "user1")
        self.assertEqual(result_1.pii.email, "user1@example.com")
        self.assertEqual(result_1.pii.name, "John Doe")

    def test_get_user_data_from_program_certificate(self):
        # Test extracting UserData from ProgramCertificateData
        result_2 = get_user_data(self.failing_status_1)
        self.assertIsNotNone(result_2)
        self.assertEqual(result_2.id, 2)
        self.assertFalse(result_2.is_active)
        self.assertEqual(result_2.pii.username, "user2")
        self.assertEqual(result_2.pii.email, "user2@example.com")
        self.assertEqual(result_2.pii.name, "Jane Doe")
