import uuid
from unittest import skip

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from credentials.apps.catalog.tests.factories import (
    CourseFactory,
    CourseRunFactory,
    OrganizationFactory,
    ProgramFactory,
)
from credentials.apps.core.tests.factories import USER_PASSWORD, UserFactory
from credentials.apps.core.tests.mixins import SiteMixin
from credentials.apps.credentials.models import UserCredential
from credentials.apps.credentials.tests.factories import (
    CourseCertificateFactory,
    ProgramCertificateFactory,
    UserCredentialFactory,
)
from apps.verifiable_credentials.issuance.models import IssuanceLine
from credentials.apps.verifiable_credentials.rest_api.v1.serializers import ProgramCredentialSerializer
from credentials.apps.verifiable_credentials.settings import vc_settings
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


class InitIssuanceViewTestCase(SiteMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.url = "/verifiable_credentials/api/v1/credentials/init/"
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
        self.program_credential_content_type = ContentType.objects.get(
            app_label="credentials", model="programcertificate"
        )
        self.program_user_credential = UserCredentialFactory.create(
            username=self.user.username,
            credential_content_type=self.program_credential_content_type,
            credential=self.program_cert,
        )
        self.wallet = vc_settings.DEFAULT_WALLET

    @skip("FIXME")
    def test_post_unauthenticated_user(self):
        response = self.client.post(self.url, {"uuid": "123456789"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @skip("FIXME")
    def test_post_with_valid_uuid_authenticated(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)
        data = {"uuid": self.program_user_credential.uuid}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        issuance = IssuanceLine.objects.last()
        self.assertEqual(response.data["deeplink"], self.wallet.create_deeplink_url(issuance.uuid))
        self.assertEqual(response.data["qrcode"], self.wallet.create_qr_code(issuance.uuid))
        self.assertEqual(response.data["app_link_android"], self.wallet.APP_LINK_ANDROID)
        self.assertEqual(response.data["app_link_ios"], self.wallet.APP_LINK_IOS)

    @skip("FIXME")
    def test_post_with_empty_uuid(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @skip("FIXME")
    def test_post_with_invalid_uuid(self):
        self.client.login(username=self.user.username, password=USER_PASSWORD)
        # FIXME: avoid this case
        with self.assertRaises(UserCredential.DoesNotExist):
            self.client.post(self.url, {"uuid": uuid.uuid4().hex})
