import base64
import gzip

from django.utils.translation import gettext as _
from rest_framework import serializers

from ..settings import vc_settings
from . import CredentialDataModel


STATUS_LIST_PURPOSE = "revocation"


class StatusEntrySchema(serializers.Serializer):
    """
    Status List 2021 Entry model.

    See: https://w3c.github.io/vc-status-list-2021/#statuslist2021entry
    """

    id = serializers.SerializerMethodField()
    type = serializers.CharField(default="StatusList2021Entry")
    statusPurpose = serializers.CharField(default=STATUS_LIST_PURPOSE)
    statusListIndex = serializers.CharField(source="status_index")
    statusListCredential = serializers.CharField(source="get_status_list_url")

    class Meta:
        read_only_fields = "__all__"

    def get_id(self, issuance_line):
        return issuance_line.get_status_list_url(hash_str=issuance_line.status_index)


class StatusList2021EntryMixin(serializers.Serializer):
    """
    Include Status List 2021 entry.
    """

    credentialStatus = StatusEntrySchema(
        source="*", help_text="https://w3c.github.io/vc-status-list-2021/#statuslist2021entry"
    )

    class Meta:
        read_only_fields = "__all__"

    @classmethod
    def get_context(cls):
        """
        Include Status List 2021 context.
        """
        return [
            "https://w3id.org/vc/status-list/2021/v1",
        ]


class StatusListSubjectSchema(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.SerializerMethodField()
    type = serializers.CharField(default="StatusList2021")
    statusPurpose = serializers.CharField(default=STATUS_LIST_PURPOSE)
    encodedList = serializers.SerializerMethodField(method_name="get_encoded_list")

    class Meta:
        read_only_fields = "__all__"

    def get_id(self, issuance_line):
        return issuance_line.get_status_list_url(hash_str="list")

    def get_encoded_list(self, issuance_line):
        return regenerate_encoded_status_sequence(issuer_id=issuance_line.issuer_id)


class StatusListDataModel(CredentialDataModel):
    """
    Status List 2021 Credential model.

    See: https://w3c.github.io/vc-status-list-2021/#statuslist2021credential
    """

    VERSION = 2021
    ID = "status-list-2021"
    NAME = _("Status List 2021")

    id = serializers.CharField(
        source="get_status_list_url", help_text="https://www.w3.org/TR/vc-data-model/#identifiers"
    )
    credentialSubject = StatusListSubjectSchema(
        source="*", help_text="https://www.w3.org/2018/credentials/#credentialSubject"
    )

    class Meta:
        read_only_fields = "__all__"

    @classmethod
    def get_context(cls):
        """
        Include Status List 2021 context.
        """
        return [
            "https://w3id.org/vc/status-list/2021/v1",
        ]

    @classmethod
    def get_types(cls):
        """
        Include Status List 2021 type.
        """
        return [
            "StatusList2021Credential",
        ]


def regenerate_encoded_status_sequence(issuer_id):
    """
    Create Status List indecies sequence from scratch for given Issuer.

    - create zero byte sequence of configured length
    - find all related to revoked credentials indicies
    - mark revoked
    - compress
    - encode
    """
    from ..issuance.models import get_revoked_indices

    status_list = bytearray(vc_settings.STATUS_LIST_LENGTH)

    for index in get_revoked_indices(issuer_id):
        status_list[index] = 1

    gzip_data = gzip.compress(status_list)
    base64_data = base64.b64encode(gzip_data)
    return base64_data.decode("utf-8")
