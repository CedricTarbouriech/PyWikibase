from __future__ import annotations

from django.db import models
from django.db.models import OneToOneField
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from model_utils.managers import InheritanceManager


class InheritanceForwardManyToOneDescriptor(ForwardManyToOneDescriptor):
    def get_queryset(self, **hints):
        return self.field.remote_field.model.objects.db_manager(hints=hints).select_subclasses()


class InheritanceForeignKey(models.ForeignKey):
    forward_related_accessor_class = InheritanceForwardManyToOneDescriptor


class Value(models.Model):
    objects = InheritanceManager()


class Entity(Value):
    def get_value(self, prop: Property) -> Value | None:
        statements = self.statements.filter(mainsnak__property=prop)
        # FIXME changer le zéro
        return statements[0].mainsnak.value if statements else None

    def add_value(self, prop: Property, value: Value, rank: int = 0) -> Statement:
        """
        Adds a statement composed of a property, a value and a rank to a subject.
        :param prop:
        :param value:
        :param rank:
        :return:
        """
        assert value.__class__ is prop.data_type.type
        snak = PropertySnak.objects.create(property=prop, type=0, value=value)
        statement = Statement(subject=self, mainsnak=snak, rank=rank)
        statement.clean_fields()
        statement.save()
        return statement

    def set_value(self, prop: Property, value: Value) -> None:
        statement = self.statements.filter(mainsnak__property=prop)
        # TODO quel comportement s’il y a plusieurs statements ?
        if statement:
            statement[0].mainsnak.value = value
            statement[0].mainsnak.save()

    def add_or_set_value(self, prop: Property, value: Value):
        statements = self.statements.filter(mainsnak__property=prop)
        if statements:
            self.set_value(prop, value)
        else:
            self.add_value(prop, value)


class DescribedEntity(Entity):
    def get_labels(self):
        return self.labels.all()

    def get_label(self, language: str):
        return self.labels.get(language=language)

    def set_label(self, language: str, text: str) -> None:
        """
        Adds a label to a described entity. Replace the label if already existing.
        :param language:
        :param text:
        :return:
        """
        if self.labels.filter(language=language).exists():
            label = self.labels.get(language=language)
            label.text = text
            label.save()
        else:
            self.labels.create(language=language, text=text)

    def add_description(self, language: str, text: str) -> None:
        if self.descriptions.filter(language=language).exists():
            description = self.descriptions.get(language=language)
            description.text = text
            description.save()
        else:
            self.descriptions.create(language=language, text=text)

    def __str__(self):
        return f': <{self.get_labels()[0]}>' if self.get_labels() else ''


class Item(DescribedEntity):
    display_id = models.IntegerField(default=1, unique=True)

    def save(self, *args, **kwargs):
        if self.pk is None:
            last_id = Item.objects.all().aggregate(largest=models.Max('display_id'))['largest']

            if last_id is not None:
                self.display_id = last_id + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Q{self.display_id}{super().__str__()}"


class Property(DescribedEntity):
    display_id = models.IntegerField(default=1, unique=True)
    data_type = models.ForeignKey('Datatype', on_delete=models.PROTECT, related_name='properties')

    def save(self, *args, **kwargs):
        if self.pk is None:
            last_id = Property.objects.all().aggregate(largest=models.Max('display_id'))['largest']

            if last_id is not None:
                self.display_id = last_id + 1

        super(Property, self).save(*args, **kwargs)

    def __str__(self):
        return f"P{self.display_id}" + super().__str__()


class PropertyType(models.IntegerChoices):
    VALUE = 0, "value"
    SOME_VALUE = 1, "somevalue"
    NO_VALUE = 2, "novalue"


class PropertySnak(models.Model):
    property = InheritanceForeignKey(Property, on_delete=models.PROTECT, related_name='using_as_property_snaks')
    type = models.IntegerField(choices=PropertyType.choices)
    # TODO: make sure that if value is instance of Datatype, it should be used by only 1 statement.
    value = InheritanceForeignKey(
        Value,
        on_delete=models.PROTECT,
        related_name='using_as_value_snaks',
        null=True,
        blank=True
    )

    def delete(self, *args, **kwargs):
        keep_value = isinstance(self.value, Entity)
        value = self.value  # stocker avant la suppression de self
        super().delete(*args, **kwargs)

        if value and not keep_value:
            value.delete()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.type == PropertyType.VALUE:
            value = self.value
        elif self.type == PropertyType.SOME_VALUE:
            value = "*somevalue*"
        elif self.type == PropertyType.NO_VALUE:
            value = "*novalue*"
        else:
            raise Exception(f"Impossible valuee for type in PropertySnak: {self.type}")
        return f"{self.property} --> {value}"


class StatementRank(models.IntegerChoices):
    VALUE = -1, "deprecated"
    SOME_VALUE = 0, "normal"
    NO_VALUE = 1, "preferred"


class Statement(models.Model):
    subject = InheritanceForeignKey(Entity, on_delete=models.CASCADE, related_name='statements')
    mainsnak = OneToOneField(PropertySnak, on_delete=models.PROTECT, related_name='used_in_statement')
    rank = models.IntegerField(choices=StatementRank)

    def delete(self, *args, **kwargs):
        mainsnak = self.mainsnak
        super().delete(*args, **kwargs)
        mainsnak.delete()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __repr__(self):
        return f"[{self.rank}] {self.subject} -- {self.mainsnak}"


class ReferenceRecord(models.Model):
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE, related_name='reference_records')


class ReferenceSnak(models.Model):
    reference = models.ForeignKey(ReferenceRecord, on_delete=models.CASCADE, related_name='snaks')
    snak = models.OneToOneField(PropertySnak, on_delete=models.CASCADE, related_name='references')


class Qualifier(models.Model):
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE, related_name='qualifiers')
    snak = models.ForeignKey(PropertySnak, on_delete=models.CASCADE)
