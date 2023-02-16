"""
Verifiable Credentials v1.1 data model.

See specification: https://www.w3.org/TR/vc-data-model/
"""
import uuid

from django.db import models
from rest_framework import serializers

from . import BaseContext, Schema


class VCContext(BaseContext):
    V1 = "https://www.w3.org/2018/credentials/v1"
    EXAMPLES_V1 = "https://www.w3.org/2018/credentials/examples/v1"


class Issuer(Schema):
    """
    Issuer schema.
    """

    id = models.CharField(max_length=255, editable=False)


class VerifiableCredential(Schema):
    """
    Verifiable Credentials data model.
    """

    context = models.JSONField(blank=True, default=VCContext.values, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False)
    # type = ["VerifiableCredential", "UniversityDegreeCredential"]
    issuer = models.OneToOneField(Issuer)
    # issuance_date = "2010-01-01T00:00:00Z"
    # subject = {
    #     "id": "did:example:ebfeb1f712ebc6f1c276e12ec21",
    #     "degree": {
    #         "type": "BachelorDegree",
    #         "name": "Bachelor of Science and Arts"
    #     }
    # }

    class Serializer(serializers.ModelSerializer):
        class Meta:
            from . import VerifiableCredential as data_model

            model = data_model
            fields = "__all__"


class VerifiableCredentialIssuanceData(Schema):
    """
    Incoming issuance request validation.

    VC API `/credentials/issue` endpoint - https://w3c-ccg.github.io/vc-api/#issue-credential

    Expected JSON-LD structure:

    {
        credential: {
            ...
        },
        options: {
            ...
        }
    }
    """
