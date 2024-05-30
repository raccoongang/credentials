from unittest import mock
from django.test import TestCase
from requests.models import Response
from credentials.apps.badges.credly.api_client import CredlyAPIClient
from credentials.apps.badges.credly.exceptions import CredlyAPIError
from credentials.apps.badges.models import CredlyOrganization
from credentials.apps.badges.credly.exceptions import CredlyError

class CredlyApiClientTestCase(TestCase):
    def setUp(self):
        self.api_client = CredlyAPIClient("test_organization_id", "test_api_key")

    def test_get_organization_nonexistent(self):
        with mock.patch("credentials.apps.badges.credly.api_client.CredlyOrganization.objects.get") as mock_get:
            mock_get.side_effect = CredlyOrganization.DoesNotExist
            with self.assertRaises(CredlyError) as cm:
                self.api_client._get_organization("nonexistent_organization_id")
            self.assertEqual(str(cm.exception), "CredlyOrganization with the uuid nonexistent_organization_id does not exist!")

    def test_perform_request(self):
        with mock.patch("credentials.apps.badges.credly.api_client.requests.request") as mock_request:
            mock_response = mock.Mock()
            mock_response.json.return_value = {"key": "value"}
            mock_request.return_value = mock_response
            result = self.api_client.perform_request("GET", "/api/endpoint")
            mock_request.assert_called_once_with("GET", "https://api.credly.com/api/endpoint", headers=self.api_client._get_headers(), json=None)
            self.assertEqual(result, {"key": "value"})

    def test_raise_for_error_success(self):
        response = mock.Mock(spec=Response)
        response.status_code = 200
        self.api_client._raise_for_error(response)

    def test_raise_for_error_error(self):
        response = mock.Mock(spec=Response)
        response.status_code = 404
        response.text = "Not Found"
        response.raise_for_status.side_effect = CredlyAPIError(f"Credly API: {response.text} ({response.status_code})")

        with self.assertRaises(CredlyAPIError) as cm:
            self.api_client._raise_for_error(response)
        self.assertEqual(str(cm.exception), "Credly API: Not Found (404)")
