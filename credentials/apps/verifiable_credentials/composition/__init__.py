"""
Composition is responsible for a construct of verifiable credential based on
different specifications (data models).
"""
from rest_framework import serializers


class BaseDataModel(serializers.BaseSerializer):
    """
    Verifiable credential common parts.
    """

    def to_representation(self, instance):
        raise NotImplementedError("Concrete data model serializers must implement their representation!")
