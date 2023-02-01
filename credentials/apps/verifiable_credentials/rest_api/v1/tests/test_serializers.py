from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from credentials.apps.catalog.tests.factories import (
    CourseFactory,
    CourseRunFactory,
    OrganizationFactory,
    ProgramFactory,
)
from credentials.apps.core.tests.factories import UserFactory
from credentials.apps.core.tests.mixins import SiteMixin
from credentials.apps.credentials.tests.factories import (
    CourseCertificateFactory,
    ProgramCertificateFactory,
    UserCredentialFactory,
)
from credentials.apps.verifiable_credentials.rest_api.v1.serializers import ProgramCredentialSerializer
from credentials.apps.verifiable_credentials.utils import get_user_program_credentials_data


class ProgramCertificatesSerializerTests(SiteMixin, TestCase):
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
            program=self.program, program_uuid=self.program.uuid, site=self.site
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

    def test_valid_data_zero_programs(self):
        self.program_cert.delete()
        self.program.delete()
        serializer = self.serialize_program_credentials()
        expected = []
        self.assertEqual(serializer, expected)

    def test_valid_data_no_program_cert(self):
        """Verify the endpoint connects if program completion is in-progress."""
        self.program_cert.delete()
        serializer = self.serialize_program_credentials()
        expected = []
        self.assertEqual(serializer, expected)

    def test_valid_data(self):
        serializer = self.serialize_program_credentials()
        expected = {
            "uuid": self.program_user_credential.uuid,
            "status": self.program_user_credential.status,
            "username": self.program_user_credential.username,
            "download_url": self.program_user_credential.download_url,
            "credential_id": self.program_user_credential.credential_id,
            "program_uuid": self.program_user_credential.credential.program_uuid.hex,
            "program_title": self.program_user_credential.credential.program.title,
        }
        self.assertEqual(serializer[0]["uuid"], str(expected["uuid"]).replace("-", ""))
        self.assertEqual(serializer[0]["status"], expected["status"])
        self.assertEqual(serializer[0]["username"], expected["username"])
        self.assertEqual(serializer[0]["download_url"], expected["download_url"])
        self.assertEqual(serializer[0]["credential_id"], expected["credential_id"])
        self.assertEqual(serializer[0]["program_uuid"], str(expected["program_uuid"]).replace("-", ""))
        self.assertEqual(serializer[0]["program_title"], expected["program_title"])
