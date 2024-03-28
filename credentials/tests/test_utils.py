import unittest

from credentials.utils import keypath

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
        payload = {
            "course": {
                "data": {
                    "identification": {
                        "id": 25
                    }
                }
            }
        }
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