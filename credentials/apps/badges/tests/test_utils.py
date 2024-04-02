import unittest
from datetime import datetime
from attr import asdict

from openedx_events.learning.data import CourseEnrollmentData, ProgramCertificateData, UserData, UserPersonalData, CourseData, ProgramData

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
        self.user_personal_data_1 = UserPersonalData(
            username="john_doe",
            email="john@example.com",
            name="John Doe"
        )

        self.user_data_1 = UserData(
            id=123,
            is_active=True,
            pii=self.user_personal_data_1
        )

        self.user_data_2 = UserData(
            id=456,
            is_active=False,
            pii=self.user_personal_data_1
        )

        self.course_data_1 = CourseData(
            course_key="course-v1:edX+DemoX+Demo_Course",
            display_name="Demo Course",
            start=datetime(2024, 1, 1),
            end=datetime(2024, 12, 31)
        )

        self.course_enrollment_1 = CourseEnrollmentData(
            user=self.user_data_1,
            course=self.course_data_1,
            mode="audit",
            is_active=True,
            creation_date=datetime.now(),
            created_by=self.user_data_1
        )

        self.program_data_1 = ProgramData(
            uuid="12345",
            title="MicroMasters in Data Science",
            program_type="microbachelors"
        )

        self.program_certificate_1 = ProgramCertificateData(
            user=self.user_data_2,
            program=self.program_data_1,
            uuid="abcdef123456",
            status="awarded",
            url="https://example.com/certificate"
        )

    def test_get_user_data_from_course_enrollment(self):
        # Test extracting UserData from CourseEnrollmentData
        result_1 = get_user_data(asdict(self.course_enrollment_1))
        self.assertIsNotNone(result_1)
        self.assertEqual(result_1.id, 123)
        self.assertTrue(result_1.is_active)
        self.assertEqual(result_1.pii.username, "john_doe")
        self.assertEqual(result_1.pii.email, "john@example.com")
        self.assertEqual(result_1.pii.name, "John Doe")

    def test_get_user_data_from_program_certificate(self):
        # Test extracting UserData from ProgramCertificateData
        result_2 = get_user_data(asdict(self.program_certificate_1))
        self.assertIsNotNone(result_2)
        self.assertEqual(result_2.id, 456)
        self.assertFalse(result_2.is_active)
        self.assertEqual(result_2.pii.username, "john_doe")
        self.assertEqual(result_2.pii.email, "john@example.com")
        self.assertEqual(result_2.pii.name, "John Doe")
