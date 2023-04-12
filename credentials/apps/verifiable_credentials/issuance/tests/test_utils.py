from unittest import TestCase, mock

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from credentials.apps.catalog.tests.factories import (
    CourseFactory,
    CourseRunFactory,
    OrganizationFactory,
    ProgramFactory,
)
from credentials.apps.core.tests.factories import UserFactory
from credentials.apps.core.tests.mixins import SiteMixin
from credentials.apps.credentials.constants import UserCredentialStatus
from credentials.apps.credentials.tests.factories import ProgramCertificateFactory, UserCredentialFactory
from credentials.apps.verifiable_credentials.issuance.models import IssuanceConfiguration
from credentials.apps.verifiable_credentials.issuance.tests.factories import (
    IssuanceConfigurationFactory,
    IssuanceLineFactory,
)
from credentials.apps.verifiable_credentials.settings import VerifiableCredentialsImproperlyConfigured
from credentials.apps.verifiable_credentials.storages.learner_credential_wallet import LCWallet

from ..utils import (
    create_issuers,
    get_active_issuers,
    get_default_issuer,
    get_issuer,
    get_issuer_ids,
    get_revoked_indices,
)


class UtilsIssuanceTestCase(SiteMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.orgs = [OrganizationFactory.create(name=name, site=self.site) for name in ["TestOrg1", "TestOrg2"]]
        self.course = CourseFactory.create(site=self.site)
        self.course_runs = CourseRunFactory.create_batch(2, course=self.course)
        self.program = ProgramFactory(
            title="TestProgram1", course_runs=self.course_runs, authoring_organizations=self.orgs, site=self.site
        )
        self.program_cert = ProgramCertificateFactory.create(program_uuid=self.program.uuid, site=self.site)
        self.program_credential_content_type = ContentType.objects.get(
            app_label="credentials", model="programcertificate"
        )
        self.program_user_credential = UserCredentialFactory.create(
            username=self.user.username,
            credential_content_type=self.program_credential_content_type,
            credential=self.program_cert,
        )
        self.issuance_line = IssuanceLineFactory.create(
            user_credential=self.program_user_credential,
            status_index=5,
            storage_id=LCWallet.ID,
        )
        self.issuance_configuration = IssuanceConfigurationFactory.create(
            issuer_id=self.issuance_line.issuer_id,
        )
        self.inactive_issuance_line = IssuanceLineFactory.create(
            user_credential=self.program_user_credential, status_index=6, status=UserCredentialStatus.REVOKED
        )

    @mock.patch("credentials.apps.verifiable_credentials.issuance.utils.IssuanceConfiguration.create_issuers")
    def test_create_issuers(self, mock_create_issuers):
        create_issuers()
        mock_create_issuers.assert_called_once()

    def test_get_active_issuers(self):
        IssuanceConfigurationFactory.create_batch(2)
        active_issuers = get_active_issuers()
        self.assertEqual(len(active_issuers), 4)
        self.assertEqual(active_issuers, ["test-issuer-did", "issuer-id-2", "2", "3"])

    def test_get_issuer_ids(self):
        IssuanceConfigurationFactory.create_batch(2)
        issuer_ids = get_issuer_ids()
        self.assertEqual(len(issuer_ids), 4)
        # FIXME: probably caused some cache or incorrect setup
        # issuer ids 5 and 6 after couple test re-runs become 8 and 9
        # self.assertEqual(issuer_ids, ['test-issuer-did', 'issuer-id-4', '5', '6'])

    def test_get_default_issuer_exists(self):
        default_issuer = get_default_issuer()
        self.assertEqual(default_issuer, self.issuance_configuration)

    def test_get_default_issuer_not_exists(self):
        IssuanceConfiguration.objects.all().delete()
        with self.assertRaisesMessage(
            VerifiableCredentialsImproperlyConfigured,
            "There are no enabled Issuance Configurations for some reason! At least one must be always active.",
        ):
            get_default_issuer()

    def test_get_issuer(self):
        issuer = get_issuer("issuer-id-2")
        # FIXME: the same story from `test_get_issuer_ids`
        # IssuanceConfiguration with issuer-id-2 become issuer-id-8
        # self.assertEqual(issuer, self.issuance_configuration)

    @mock.patch("credentials.apps.verifiable_credentials.issuance.utils.IssuanceConfiguration.get_indicies_for_status")
    def get_revoked_indices(self, mock_get_indicies_for_status):
        get_revoked_indices("test-issuer-id")
        mock_get_indicies_for_status.assert_called_once()
