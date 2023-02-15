import base64
from io import BytesIO

import qrcode
from django.contrib.contenttypes.models import ContentType

from credentials.apps.credentials.api import get_user_credentials_by_content_type
from credentials.apps.credentials.data import UserCredentialStatus


def get_user_program_credentials_data(username):
    """
    Translates a list of UserCredentials (for programs) into context data.

    Arguments:
        request_username(str): Username for whom we are getting UserCredential objects for

    Returns:
        list(dict): A list of dictionaries, each dictionary containing information for a credential that the
        user awarded
    """
    program_cert_content_type = ContentType.objects.get(app_label="credentials", model="programcertificate")
    program_credentials = get_user_credentials_by_content_type(
        username, [program_cert_content_type], UserCredentialStatus.AWARDED.value
    )

    return [
        {
            "uuid": credential.uuid.hex,
            "status": credential.status,
            "username": credential.username,
            "download_url": credential.download_url,
            "credential_id": credential.credential_id,
            "program_uuid": credential.credential.program_uuid.hex,
            "program_title": credential.credential.program.title,
        }
        for credential in program_credentials
    ]


def generate_base64_qr_code(text):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10)
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image()
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str
