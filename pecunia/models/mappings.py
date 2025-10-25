from __future__ import annotations

from django.db import models

from pecunia.models import Property, Item


class UnknownMappingException(Exception):
    pass


class Mapping(models.Model):
    class Meta:
        abstract = True

    key = models.CharField(max_length=255, unique=True)

    @classmethod
    def get(cls, key: str):
        """
        Returns the element associated with the given key.
        :param key: the key associated with the mapping
        :raise UnknownMappingException: if the mapping does not exist
        :return: the element associated with the given key
        """
        raise NotImplementedError("Mapping.get not implemented")

    @classmethod
    def has(cls, key: str) -> bool:
        """
        Checks if there is a mapping for the given key.
        :param key: the key to check
        :return: True if there is a mapping, False otherwise
        """
        return cls.objects.filter(key=key).exists()


class ItemMapping(Mapping):
    """
    Maps symbolic keys to be used in code to the corresponding item.
    """
    item = models.OneToOneField(Item, on_delete=models.PROTECT, blank=True, null=True)

    @classmethod
    def get(cls, key: str):
        try:
            return cls.objects.get(key=key).item
        except cls.DoesNotExist:
            raise UnknownMappingException(f"Item mapping '{key}' does not exist.")


class PropertyMapping(Mapping):
    """
    Maps symbolic keys to be used in code to the corresponding property.
    """
    property = models.OneToOneField(Property, on_delete=models.PROTECT, blank=True, null=True)

    @classmethod
    def get(cls, key: str):
        try:
            return cls.objects.get(key=key).property
        except cls.DoesNotExist:
            raise UnknownMappingException(f"Property mapping '{key}' does not exist.")
