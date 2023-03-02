from django.db.models.signals import post_save
from django.dispatch import receiver

from credentials.apps.credentials.models import UserCredential

from .composition.status_list import StatusListDataModel, revoke_items
from .models import IssuanceLine


# def generate_status_list_on_status_revoke(instance, created, **kwargs):
#     if "status" in kwargs.get('update_fields') and instance.status == UserCredential.REVOKED:
#         issuance_line = IssuanceLine.objects.filter(processed=True, user_credential=instance).last()

#         if issuance_line:
#             status_list = StatusListDataModel(data={"issuer": issuance_line.issuer_id})
#             status_list.is_valid()
#             status_list.save()

# post_save.connect(
#     generate_status_list_on_status_revoke,
#     sender=UserCredential,
#     dispatch_uid="post_save_user_credential_generate_status_list"
# )

@receiver(post_save, sender=UserCredential)
def update_issuance_lines(instance, created, **kwargs):
    user_credential = instance

    # there are no verifiable credentials yet for a newly created user credential:
    if created:
        return

    # not interested in anything but "revocation":
    if user_credential.status != UserCredential.REVOKED:
        return

    # find all related issuance lines and switch status:
    issuance_lines = IssuanceLine.objects.filter(user_credential=user_credential)
    updated = issuance_lines.update(status=IssuanceLine.REVOKED)

    # process revocation flow:
    if updated:
        revoke_items(positions=issuance_lines.values_list('status_index', flat=True))



