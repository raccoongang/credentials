"""
Composition is responsible for a construct of verifiable credential based on
different specifications (data models).
"""
from enum import Enum
from django.db import models


class BaseContext(Enum):

    @classmethod
    def values(cls):
        return [item.value for item in cls]


class Schema(models.Model):
    """
    All VC data models are unmanaged.
    """
    class Meta:
        abstract = True
        managed = False