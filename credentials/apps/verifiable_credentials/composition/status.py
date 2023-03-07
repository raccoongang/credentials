import base64
import gzip
import json
import os
from datetime import datetime

from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework import serializers

from credentials.apps.credentials.models import UserCredential

from ..models import IssuanceLine
from ..settings import vc_settings
from . import BaseDataModel


def make_status_list_path(issuer_did):
    return f"{settings.ROOT_URL}{vc_settings.STATUS_LIST['PUBLIC_PATH']}{issuer_did}.json"


class _StatusEntryDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.SerializerMethodField(method_name="get_id", read_only=True)
    statusListIndex = serializers.CharField(source="status_index", read_only=True)
    statusListCredential = serializers.SerializerMethodField(method_name="get_list_credential", read_only=True)
    type = serializers.SerializerMethodField()
    statusPurpose = serializers.SerializerMethodField(method_name="get_status_purpose", read_only=True)

    def get_status_purpose(self, *args, **kwargs):
        return "revocation"

    def get_type(self, *args, **kwargs):
        return "StatusList2021Entry"

    def get_id(self, issuance_line):
        return f"{make_status_list_path(issuance_line.issuer_id)}#{issuance_line.status_index}"

    def get_list_credential(self, issuance_line):
        return make_status_list_path(issuance_line.issuer_id)


class StatusEntryDataModelMixin(serializers.Serializer):  # pylint: disable=abstract-method
    credentialStatus = serializers.SerializerMethodField(method_name="get_status", read_only=True)

    def get_status(self, issuance_line):
        return _StatusEntryDataModel(issuance_line).data

    @property
    def context(self):
        return ["https://w3id.org/vc/status-list/2021/v1"]


class SubjectDataModel(serializers.Serializer):  # pylint: disable=abstract-method
    id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    statusPurpose = serializers.SerializerMethodField(method_name="get_status_purpose")
    encodedList = serializers.SerializerMethodField(method_name="get_encoded_list")

    def get_status_purpose(self, *args, **kwargs):
        return "revocation"

    def get_type(self, *args, **kwargs):
        return "StatusList2021"

    def get_id(self, *args, **kwargs):
        return f"{make_status_list_path(self.validated_data.get('issuer'))}#list"

    def validate(self, attrs):
        return attrs

    def get_encoded_list(self, *args, **kwargs):
        status_list = bytearray(vc_settings.STATUS_LIST["LENGTH"])

        issuance_lines = IssuanceLine.objects.filter(
            issuer_id=self.validated_data.get("issuer"),
            user_credential__status=UserCredential.REVOKED,
            processed=True,
            status_index__gte=0,
        )

        for line in issuance_lines:
            status_list[line.status_index] = 1

        gzip_data = gzip.compress(status_list)
        base64_data = base64.b64encode(gzip_data)

        return base64_data.decode("utf-8")


class StatusListDataModel(BaseDataModel):  # pylint: disable=abstract-method
    id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    issuanceDate = serializers.SerializerMethodField(method_name="get_issuance_date")
    issuer = serializers.CharField()
    credentialSubject = serializers.SerializerMethodField(method_name="get_subject")

    def get_issuance_date(self, *args, **kwargs):
        return str(datetime.now())

    def get_subject(self, *args, **kwargs):
        subject = SubjectDataModel(data=self.validated_data)
        subject.is_valid()
        return subject.data

    def get_id(self, *args, **kwargs):
        return make_status_list_path(self.validated_data.get("issuer"))

    def get_type(self, *args, **kwargs):
        return ["VerifiableCredential", "StatusList2021Credential"]

    @property
    def context(self):
        return [
            "https://www.w3.org/2018/credentials/v1",
            "https://w3id.org/vc/status-list/2021/v1",
        ]

    def validate(self, attrs):
        return attrs

    def save(self, *args, **kwargs):
        path = os.path.join(vc_settings.STATUS_LIST["PUBLIC_ROOT"], f"{self.validated_data.get('issuer')}.json")
        # FIXME: folders must be created
        with default_storage.open(path, "w") as file:
            file.write(json.dumps(self.data, indent=2))
