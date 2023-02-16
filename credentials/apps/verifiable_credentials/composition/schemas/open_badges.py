"""
Open Badges 3.0 data model.

See specification: https://1edtech.github.io/openbadges-specification/ob_v3p0.html
"""
import uuid

from django.db import models

from . import BaseContext, Schema
from .verifiable_credentials import VCContext


class OBContext(BaseContext):
    VC_V1 = VCContext.V1.value
    V3P0 = "https://purl.imsglobal.org/spec/ob/v3p0/context.json"


class OpenBadge(Schema):
    """
    Open Badges data model.
    """
    context = models.JSONField(blank=True, default=OBContext.values)
    id = models.UUIDField(default=uuid.uuid4, editable=False)