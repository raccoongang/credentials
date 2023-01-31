from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from credentials.apps.catalog.tests.factories import (
    CourseFactory,
    CourseRunFactory,
    OrganizationFactory,
    ProgramFactory,
)
from credentials.apps.core.tests.factories import USER_PASSWORD, UserFactory
from credentials.apps.core.tests.mixins import SiteMixin
from credentials.apps.credentials.tests.factories import (
    CourseCertificateFactory,
    ProgramCertificateFactory,
    UserCredentialFactory,
)
from credentials.apps.verifiable_credentials.rest_api.v1.serializers import ProgramCredentialSerializer
from credentials.apps.verifiable_credentials.utils import get_user_program_credentials_data


class ProgramCredentialsViewTests(SiteMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.orgs = [OrganizationFactory.create(name=name, site=self.site) for name in ["TestOrg1", "TestOrg2"]]
        self.course = CourseFactory.create(site=self.site)
        self.course_runs = CourseRunFactory.create_batch(2, course=self.course)
        self.program = ProgramFactory(
            title="TestProgram1", course_runs=self.course_runs, authoring_organizations=self.orgs, site=self.site
        )
        self.course_certs = [
            CourseCertificateFactory.create(
                course_id=course_run.key,
                site=self.site,
            )
            for course_run in self.course_runs
        ]
        self.program_cert = ProgramCertificateFactory.create(
            program=self.program,
            program_uuid=self.program.uuid,
            site=self.site,
        )
        self.course_credential_content_type = ContentType.objects.get(
            app_label="credentials", model="coursecertificate"
        )
        self.program_credential_content_type = ContentType.objects.get(
            app_label="credentials", model="programcertificate"
        )
        self.course_user_credentials = [
            UserCredentialFactory.create(
                username=self.user.username,
                credential_content_type=self.course_credential_content_type,
                credential=course_cert,
            )
            for course_cert in self.course_certs
        ]
        self.program_user_credential = UserCredentialFactory.create(
            username=self.user.username,
            credential_content_type=self.program_credential_content_type,
            credential=self.program_cert,
        )

    def serialize_program_credentials(self):
        request = APIRequestFactory(SERVER_NAME=self.site.domain).get("/")
        return ProgramCredentialSerializer(
            get_user_program_credentials_data(self.user.username),
            context={"request": request},
            many=True,
        ).data

    def test_deny_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get("/verifiable_credentials/api/v1/program_credentials/")
        self.assertEqual(response.status_code, 401)

    def test_allow_authenticated_user(self):
        """Verify the endpoint requires an authenticated user."""
        self.client.logout()
        self.client.login(username=self.user.username, password=USER_PASSWORD)
        response = self.client.get("/verifiable_credentials/api/v1/program_credentials/")
        self.assertEqual(response.status_code, 200)

    def test_get(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)
        response = self.client.get("/verifiable_credentials/api/v1/program_credentials/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["program_credentials"], self.serialize_program_credentials())


@override_settings(ENABLE_VERIFIABLE_CREDENTIALS=True)
class VCIssuanceQRCodeViewTestCase(SiteMixin, TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.url = "/verifiable_credentials/api/v1/qrcode/"

    # FIXME: authentication_classes don't work properly
    # def test_post_unauthenticated_user(self):
    #     data = {"uuid": "123456789"}
    #     response = self.client.post(self.url, data)

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_with_valid_uuid_authenticated(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)

        data = {"uuid": "123456789"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"qrcode": "<base64-encoded-content>"})

    def test_post_with_invalid_uuid(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)

        data = {}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(ENABLE_VERIFIABLE_CREDENTIALS=True)
class VCIssuanceDeeplinkViewTestCase(SiteMixin, TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.url = "/verifiable_credentials/api/v1/deeplink/"

    # FIXME: authentication_classes don't work properly
    # def test_post_unauthenticated_user(self):
    #     data = {"uuid": "123456789"}
    #     response = self.client.post(self.url, data)

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_with_valid_uuid_authenticated(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)

        data = {"uuid": "123456789"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"deeplink": "<parametrized-deep-link>"})

    def test_post_with_invalid_uuid(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)

        data = {}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(ENABLE_VERIFIABLE_CREDENTIALS=True, VC_DEFAULT_STANDARD="test_vc_format")
class VCIssuanceWalletViewTestCase(SiteMixin, TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.url = "/verifiable_credentials/api/v1/wallet/"

    # FIXME: authentication_classes don't work properly
    # def test_get_deny_unauthenticated_user(self):
    #     response = self.client.get(self.url)

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_allow_authenticated_user(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"document_format": "test_vc_format"})
