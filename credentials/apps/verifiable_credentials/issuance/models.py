"""
Verifiable Credentials DB models.
"""
import uuid
from urllib.parse import urljoin

from crum import get_current_request
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from credentials.apps.credentials.models import UserCredential

from ..composition.utils import get_data_model, get_data_models
from ..settings import vc_settings
from ..storages.utils import get_storage


def generate_data_model_choices():
    return [(data_model.ID, data_model.NAME) for data_model in get_data_models()]


class IssuanceLine(TimeStampedModel):
    """
    Specific verifiable credential issuance details (issuance line).

    .. no_pii:
    """

    # Initial data:
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_credential = models.ForeignKey(
        UserCredential,
        null=True,
        blank=True,
        related_name="vc_issues",
        on_delete=models.PROTECT,
        help_text=_("Related Open edX learner credential"),
    )
    processed = models.BooleanField(default=False, help_text=_("Completeness indicator"))
    issuer_id = models.CharField(max_length=255, help_text=_("Issuer DID"))
    storage_id = models.CharField(max_length=128, help_text=_("Target storage identifier"))
    # Storage request data:
    subject_id = models.CharField(
        max_length=255,
        help_text=_("Verifiable credential subject DID"),
    )
    data_model_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Verifiable credential specification to use"),
        choices=generate_data_model_choices(),
    )
    expiration_date = models.DateTimeField(null=True, blank=True, db_index=True)
    status_index = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Defines a position in the Status List sequence"),
    )
    status = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Keeps track on a corresponding user credential's status"),
    )

    class Meta:
        ordering = ("created",)
        unique_together = ("issuer_id", "status_index")

    def __str__(self):
        return (
            f"IssuanceLine(user_credential={self.user_credential}, "
            f"issuer_id={self.issuer_id}, storage_id={self.storage_id})"
        )

    @property
    def storage(self):
        return get_storage(self.storage_id)

    @property
    def data_model(self):
        return get_data_model(self.data_model_id)

    @property
    def data_model_name(self):
        return self.data_model and self.data_model.NAME

    @property
    def issuer_name(self):
        from .utils import get_issuer  # pylint: disable=import-outside-toplevel

        return getattr(get_issuer(self.issuer_id), "issuer_name", None)

    @property
    def credential_name(self):
        """
        Map internal credential types to verbose labels (source models do not provide those).
        """
        if credential_title := self.user_credential.credential.title:
            return credential_title

        program_certificate_name = (
            _("Program Certificate")
            if not self.program
            else _("Program Certificate for passing a program {program_title}").format(program_title=self.program.title)
        )
        course_certificate = _("Course Certificate")

        type_to_name = {
            "programcertificate": program_certificate_name,
            "coursecertificate": course_certificate,
        }
        return type_to_name.get(self.credential_type)

    @property
    def credential_type(self):
        return self.user_credential.credential_content_type.model

    @property
    def program(self):
        return getattr(self.user_credential.credential, "program", None)

    def construct(self, context):
        serializer = self.data_model(self, context=context)
        return serializer.data

    def finalize(self):
        self.processed = True
        self.save()

    def get_status_list_url(self, hash_str=None):
        request = get_current_request()
        if not request:
            return None

        base_url = request.build_absolute_uri().split(request.path)[0]
        status_list_url = urljoin(
            base_url,
            reverse(
                "verifiable_credentials:api:v1:status-list-2021-v1",
                kwargs={"issuer_id": self.issuer_id},
            ),
        )
        if hash_str is None:
            return status_list_url

        return f"{status_list_url}#{hash_str}"

    @classmethod
    def resolve_issuer(cls):
        """
        Unconditionally (for now) returns system-level Issier ID.
        """
        from .utils import get_default_issuer  # pylint: disable=import-outside-toplevel

        return get_default_issuer()

    @classmethod
    def get_next_status_index(cls, issuer_id):
        """
        Return next status list position for given Issuer.
        """
        last = cls.objects.filter(issuer_id=issuer_id, status_index__gte=0).order_by("status_index").last()
        if not last:
            return 0
        return last.status_index + 1

    @classmethod
    def get_indicies_for_status(cls, *, issuer_id, status):
        """
        Status indicies with revoked credentials for given Issuer.
        """
        return list(
            cls.objects.filter(
                issuer_id=issuer_id,
                user_credential__status=status,
                processed=True,
                status_index__gte=0,
            )
            .order_by("status_index")
            .values_list("status_index", flat=True)
        )


class IssuanceConfiguration(TimeStampedModel):
    """
    Verifiable credentials issuer configuration.

    The model stores a details needed to compose and issue verifiable credentials.

    .. no_pii:

    NOTE:
        - current issuer by default has a system-wide scope;
        - it is expected an explicit `scope` ("system"|"site"|"org"|"course") field will be used in the future;
        - additional issuer preferences may live here as well (credential claims, storages filtering, etc.);
    """

    enabled = models.BooleanField(default=False)
    issuer_id = models.CharField(primary_key=True, max_length=255, help_text=_("Issuer DID"))
    issuer_key = models.JSONField(
        help_text=_("Issuer secret key. See: https://w3c-ccg.github.io/did-method-key/#ed25519-x25519")
    )
    issuer_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ("enabled", "created")

    @classmethod
    def create_issuers(cls):
        """
        Create issuance configuration(s) from deployment configuration.

        Top level scope issuer is the must (auto-created).
        """
        return IssuanceConfiguration.objects.update_or_create(
            issuer_id=vc_settings.DEFAULT_ISSUER.get("ID"),
            issuer_key=vc_settings.DEFAULT_ISSUER.get("KEY"),
            defaults={
                "enabled": True,
                "issuer_name": vc_settings.DEFAULT_ISSUER.get("NAME"),
            },
        )
