from unittest import TestCase, mock

from django.test import TestCase

from ..status_list import issue_status_list


class StatusListIssuanceTestCase(TestCase):
    @mock.patch("credentials.apps.verifiable_credentials.issuance.status_list.CredentialIssuer")
    def test_issue_status_list_sequence(self, mock_credential_issuer):
        mock_credential_issuer.return_value.issue.return_value = "dummy-credential"
        result = issue_status_list(issuer_id="mock-issuer")
        mock_credential_issuer.assert_called_once_with(issuance_uuid=mock_credential_issuer.init().uuid)
        mock_credential_issuer.return_value.issue.assert_called_once()
        self.assertEqual(result, "dummy-credential")
