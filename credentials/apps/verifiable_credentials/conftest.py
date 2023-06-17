"""
Pytest: Verifiable Credentials base testing config/fixtures.
"""
import pytest


TEST_ISSUER_CONFIG = {
    "ID": "test-issuer-did",
    "KEY": "test-issuer-key",
    "NAME": "test-issuer-name",
}


@pytest.fixture(autouse=True)
def vc_enabled(settings):
    settings.ENABLE_VERIFIABLE_CREDENTIALS = True


@pytest.fixture()
def vc_disabled(settings):
    settings.ENABLE_VERIFIABLE_CREDENTIALS = False


@pytest.fixture()
def verifiable_credentials_data_model():
    return "credentials.apps.verifiable_credentials.composition.verifiable_credentials.VerifiableCredentialsDataModel"


@pytest.fixture()
def open_badges_data_model():
    return "credentials.apps.verifiable_credentials.composition.open_badges.OpenBadgesDataModel"


@pytest.fixture()
def status_list_data_model():
    return "credentials.apps.verifiable_credentials.composition.status_list.StatusListDataModel"


@pytest.fixture()
def issuance_line_serializer():
    return "credentials.apps.verifiable_credentials.issuance.serializers.IssuanceLineSerializer"


@pytest.fixture()
def learner_credentials_storage():
    return "credentials.apps.verifiable_credentials.storages.learner_credential_wallet.LCWallet"


@pytest.fixture()
def default_issuer_config():
    return TEST_ISSUER_CONFIG
