from __future__ import annotations

from django.db import models

from pecunia.models import Item, PropertyMapping, ItemMapping, MonolingualTextValue


class DocumentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            statements__mainsnak__property=PropertyMapping.get('is_a'),
            statements__mainsnak__value=ItemMapping.get('document')
        )


class Document(Item):
    objects = DocumentManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs) -> None:
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            self.add_value(
                PropertyMapping.get('is_a'),
                ItemMapping.get('document')
            )

    @classmethod
    def get_by_id(cls, display_id: int) -> Document:
        return cls.objects.get(display_id=display_id,
                               statements__mainsnak__property=PropertyMapping.get('is_a'),
                               statements__mainsnak__value=ItemMapping.get('document'))

    def set_title(self, title) -> None:
        self.add_or_set_value(PropertyMapping.get('title'), title)

    def get_title(self) -> MonolingualTextValue:
        return self.statements.get(mainsnak__property=PropertyMapping.get('title')).mainsnak.value

    def set_author(self, author) -> None:
        self.add_or_set_value(PropertyMapping.get('author'), author)

    def set_author_function(self, author_function) -> None:
        self.add_or_set_value(PropertyMapping.get('author_function'), author_function)

    def set_text(self, text: MonolingualTextValue) -> None:
        self.add_or_set_value(PropertyMapping.get('text'), text)

    def set_translation(self, translation: MonolingualTextValue) -> None:
        self.add_or_set_value(PropertyMapping.get('translation'), translation)

    def set_provenance(self, provenance: Item) -> None:
        self.add_or_set_value(PropertyMapping.get('provenance'), provenance)

    def set_source_type(self, source_type: Item) -> None:
        self.add_or_set_value(PropertyMapping.get('source_type'), source_type)
