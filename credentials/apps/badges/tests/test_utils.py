import unittest
from datetime import datetime
from attr import asdict

from openedx_events.learning.data import UserData, UserPersonalData, CourseData, CoursePassingStatusData

from ..utils import extract_payload, keypath, get_user_data, is_datapath_valid


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


class TestKeypathCheck(unittest.TestCase):
    def setUp(self):
        self.event_type = "org.openedx.learning.course.passing.status.updated.v1"

    def test_datapath_valid_success(self):
        is_valid = is_datapath_valid("course_passing_status.user.pii.username", self.event_type)
        self.assertTrue(is_valid)

    def test_datapath_valid_failure(self):
        is_valid = is_datapath_valid("course_passing_status.user.username", self.event_type)
        self.assertFalse(is_valid)


class TestGetUserData(unittest.TestCase):
    def setUp(self):
        self.course_data_1 = CourseData(
            course_key="CS101",
            display_name="Introduction to Computer Science",
            start=datetime(2024, 4, 1),
            end=datetime(2024, 6, 1),
        )
        self.user_data_1 = UserData(
            id=1, is_active=True, pii=UserPersonalData(username="user1", email="user1@example.com", name="John Doe")
        )

        self.course_data_2 = CourseData(
            course_key="PHY101",
            display_name="Introduction to Physics",
            start=datetime(2024, 4, 15),
            end=datetime(2024, 7, 15),
        )
        self.user_data_2 = UserData(
            id=2, is_active=False, pii=UserPersonalData(username="user2", email="user2@example.com", name="Jane Doe")
        )

        self.passing_status_1 = {
            "course_passing_status": CoursePassingStatusData(
                status=CoursePassingStatusData.PASSING, course=self.course_data_1, user=self.user_data_1
            )
        }

    def test_get_user_data_from_course_enrollment(self):
        result_1 = get_user_data(extract_payload(self.passing_status_1))
        self.assertIsNotNone(result_1)
        self.assertEqual(result_1.id, 1)
        self.assertTrue(result_1.is_active)
        self.assertEqual(result_1.pii.username, "user1")
        self.assertEqual(result_1.pii.email, "user1@example.com")
        self.assertEqual(result_1.pii.name, "John Doe")


class TestExtractPayload(unittest.TestCase):
    def setUp(self):
        self.course_data = CourseData(
            course_key="105-3332",
            display_name="Introduction to Computer Science",
            start=datetime(2024, 4, 1),
            end=datetime(2024, 6, 1),
        )

    def test_extract_payload_as_dict_false(self):
        public_signal_kwargs = {
            "public_signal_kwargs": {"course": self.course_data},
            "as_dict": False,
        }
        expected_result = {"course": self.course_data}
        result = extract_payload(**public_signal_kwargs)
        self.assertEqual(result, expected_result)

    def test_extract_payload_as_dict_true(self):
        public_signal_kwargs = {
            "public_signal_kwargs": {"course": self.course_data},
            "as_dict": True,
        }
        expected_result = {"course": asdict(self.course_data)}
        result = extract_payload(**public_signal_kwargs)
        self.assertEqual(result, expected_result)

    def test_extract_payload_empty_payload(self):
        public_signal_kwargs = {"public_signal_kwargs": {}, "as_dict": False}
        result = extract_payload(**public_signal_kwargs)
        self.assertIsNone(result)
