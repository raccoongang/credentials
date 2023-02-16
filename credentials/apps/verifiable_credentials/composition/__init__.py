"""
Composition is responsible for a construct of verifiable credential based on
different specifications (data models).
"""
from django.db import models


class Schema(models.Model):
    """
    All VC data models are unmanaged.
    """
    class Meta:
        abstract = True
        managed = False