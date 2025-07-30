from __future__ import annotations

from django.db import models

from wikibase.models import Property, Item


class UnknownMappingException(Exception):
    pass


class Mapping(models.Model):
    class Meta:
        abstract = True

    key = models.CharField(max_length=255, unique=True)

    @classmethod
    def get(cls, key: str):
        raise NotImplementedError("Mapping.get not implemented")

    @classmethod
    def has(cls, key: str) -> bool:
        return cls.objects.filter(key=key).exists()


class PropertyMapping(Mapping):
    """
    Maps symbolic keys to be used in code to the corresponding property.
    """
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, blank=True, null=True)

    @classmethod
    def get(cls, key: str):
        try:
            return cls.objects.get(key=key).property
        except cls.DoesNotExist:
            raise UnknownMappingException(f"Property mapping '{key}' does not exist.")


class ItemMapping(Mapping):
    """
    Maps symbolic keys to be used in code to the corresponding item.
    """
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)

    @classmethod
    def get(cls, key: str):
        try:
            return cls.objects.get(key=key).item
        except cls.DoesNotExist:
            raise UnknownMappingException(f"Item mapping '{key}' does not exist.")
