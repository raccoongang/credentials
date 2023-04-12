import base64
import gzip
from unittest import TestCase, mock

from django.test import TestCase

from ..status_list import regenerate_encoded_status_sequence


class StatusListCompositionTestCase(TestCase):
    @mock.patch("credentials.apps.verifiable_credentials.issuance.utils.get_revoked_indices")
    def test_regenerate_encoded_status_sequence(self, mock_get_revoked_indices):
        mock_get_revoked_indices.return_value = [1, 3, 5]
        result = regenerate_encoded_status_sequence("test")
        decoded_data = base64.b64decode(result)
        decompressed_data = gzip.decompress(decoded_data)
        status_list = bytearray(decompressed_data)

        for i in range(5):
            if i in mock_get_revoked_indices.return_value:
                self.assertEqual(status_list[i], 1)
            else:
                self.assertEqual(status_list[i], 0)
