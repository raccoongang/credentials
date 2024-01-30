import base64
import logging
from functools import lru_cache
from urllib.parse import urljoin

import requests
from attrs import asdict
from django.conf import settings
from requests.exceptions import HTTPError
from .exceptions import CredlyAPIError


logger = logging.getLogger(__name__)


class CredlyAPIClient:
    """
    A client for interacting with the Credly API.

    This class provides methods for performing various operations on the Credly API,
    such as fetching organization details, fetching badge templates, issuing badges,
    and revoking badges.

    TODO: improve client to return data in a more usable format
    """

    def __init__(self, organization_id, api_key):
        """
        Initializes a CredlyRestAPI object.

        Args:
            organization_id (str): ID of the organization.
            api_key (str): API key for authentication.
        """

        self.organization_id = organization_id
        self.api_key = api_key
        self.base_api_url = urljoin(settings.CREDLY_API_BASE_URL, f"organizations/{self.organization_id}/")

    def perform_request(self, method, url_suffix, data=None):
        """
        Perform an HTTP request to the specified URL suffix.

        Args:
            method (str): HTTP method to use for the request.
            url_suffix (str): URL suffix to append to the base Credly API URL.
            data (dict, optional): Data to send with the request.

        Returns:
            dict: JSON response from the API.

        Raises:
            requests.HTTPError: If the API returns an error response.
        """
        url = urljoin(self.base_api_url, url_suffix)
        response = requests.request(method.upper(), url, headers=self._get_headers(), data=data)
        self._raise_for_error(response)
        return response.json()

    def fetch_organization(self):
        """
        Fetches the organization from the Credly API.
        """
        return self.perform_request("get", "")

    def fetch_badge_templates(self):
        """
        Fetches the badge templates from the Credly API.
        """
        return self.perform_request("get", "badge_templates/")

    def issue_badge(self, issue_badge_data):
        """
        Issues a badge using the Credly REST API.

        Args:
            issue_badge_data (IssueBadgeData): Data required to issue the badge.
        """
        return self.perform_request("post", "badges/", asdict(issue_badge_data))

    def revoke_badge(self, badge_id):
        """
        Revoke a badge with the given badge ID.

        Args:
            badge_id (str): ID of the badge to revoke.
        """
        return self.perform_request("put", f"badges/{badge_id}/revoke/")

    def _raise_for_error(self, response):
        """
        Raises a CredlyAPIError if the response status code indicates an error.

        Args:
            response (requests.Response): Response object from the Credly API request.

        Raises:
            CredlyAPIError: If the response status code indicates an error.
        """
        try:
            response.raise_for_status()
        except HTTPError:
            logger.error(f"Error while processing credly api request: {response.status_code} - {response.text}")
            raise CredlyAPIError

    def _get_headers(self):
        """
        Returns the headers for making API requests to Credly.
        """
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Basic {self._build_authorization_token()}",
        }

    @lru_cache
    def _build_authorization_token(self):
        """
        Build the authorization token for the Credly API.

        Returns:
            str: Authorization token.
        """
        return base64.b64encode(self.api_key.encode("ascii")).decode("ascii")
