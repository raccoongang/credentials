from django.db.models.signals import post_save

from credentials.apps.credentials.models import UserCredential
from credentials.apps.verifiable_credentials.composition.status import StatusListDataModel

from .models import IssuanceLine


def generate_status_list_on_status_revoke(instance, created, **kwargs):
    if "status" in kwargs.get('update_fields') and instance.status == UserCredential.REVOKED:
        issuance_line = IssuanceLine.objects.filter(processed=True, user_credential=instance).last()

        if issuance_line:
            status_list = StatusListDataModel(data={"issuer": issuance_line.issuer_id})
            status_list.is_valid()
            status_list.save()

post_save.connect(
    generate_status_list_on_status_revoke,
    sender=UserCredential,
    dispatch_uid="post_save_user_credential_generate_status_list"
)
