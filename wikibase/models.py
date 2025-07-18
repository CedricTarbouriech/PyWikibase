from __future__ import annotations

from django.core import exceptions
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from model_utils.managers import InheritanceManager


class InheritanceForwardManyToOneDescriptor(ForwardManyToOneDescriptor):
    def get_queryset(self, **hints):
        return self.field.remote_field.model.objects.db_manager(hints=hints).select_subclasses()


class InheritanceForeignKey(models.ForeignKey):
    forward_related_accessor_class = InheritanceForwardManyToOneDescriptor


def positive(v: float | int) -> None:
    if v < 0:
        raise exceptions.ValidationError(f'expected v >= 0, got {v}', 'positive')


class IriField(models.TextField):
    pass


class Value(models.Model):
    objects = InheritanceManager()


class Entity(Value):
    identifier = IriField()


class Datatype(Entity):
    class_name = models.CharField(max_length=50)

    def validate_constraints(self, exclude=None):
        if exclude and 'class_name' not in exclude:
            if not issubclass(self.type, Value):
                raise exceptions.ValidationError(
                    'invalid value for class_name',
                    'Datatype.class_name type error'
                )

    @property
    def type(self) -> type[Value]:
        return globals()[self.class_name]

    def __str__(self):
        return f'Datatype[{self.class_name}]'

    def __repr__(self):
        return f'Datatype[{self.class_name}]'


class DescribedEntity(Entity):
    labels = models.ForeignKey('MultilingualTextValue', on_delete=models.PROTECT, related_name='labelled_items')
    descriptions = models.ForeignKey('MultilingualTextValue', on_delete=models.PROTECT, related_name='described_items')
    aliases = models.ForeignKey('MultilingualMultiTextValue', on_delete=models.PROTECT, related_name='aliased_items')

    def get_labels(self):
        return self.labels.monolingualtextvalue_set.all()

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.labels = MultilingualTextValue.objects.create()
            self.descriptions = MultilingualTextValue.objects.create()
            self.aliases = MultilingualMultiTextValue.objects.create()
        super().save(*args, **kwargs)

    def __str__(self):
        return f': <{self.get_labels()[0]}>' if self.get_labels() else ''


class Item(DescribedEntity):
    display_id = models.IntegerField(default=1, unique=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            last_id = Item.objects.all().aggregate(largest=models.Max('display_id'))['largest']

            if last_id is not None:
                self.display_id = last_id + 1

        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return f"Q{self.display_id}{super().__str__()}"


class Property(DescribedEntity):
    display_id = models.IntegerField(default=1, unique=True)
    data_type = models.ForeignKey(Datatype, on_delete=models.PROTECT, related_name='properties')

    def __str__(self):
        return f"P{self.display_id}" + super().__str__()

    def save(self, *args, **kwargs):
        if self._state.adding:
            last_id = Property.objects.all().aggregate(largest=models.Max('display_id'))['largest']

            if last_id is not None:
                self.display_id = last_id + 1

        super(Property, self).save(*args, **kwargs)


class Snak(models.Model):
    objects = InheritanceManager()


class PropertySnak(Snak):
    property = InheritanceForeignKey(Property, on_delete=models.PROTECT)
    # Null if main snak, non-null if auxiliary snak
    statement = models.ForeignKey('Statement', on_delete=models.CASCADE, null=True, blank=True)


class PropertyValueSnak(PropertySnak):
    value = InheritanceForeignKey(Value, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.property} --> {self.value}"


class PropertySomeValueSnak(PropertySnak):
    pass


class PropertyNoValueSnak(PropertySnak):
    pass


class Statement(models.Model):
    subject = InheritanceForeignKey(Entity, on_delete=models.CASCADE)
    mainSnak = InheritanceForeignKey(Snak, on_delete=models.CASCADE, related_name='statements')
    rank = models.IntegerField(choices=((-1, "Deprecated"), (0, "Normal"), (1, "Preferred")),
                               validators=[MinValueValidator(-1), MaxValueValidator(1)])

    def __repr__(self):
        return f"[{self.rank}] {self.subject} -- {self.mainSnak}"


class ReferenceRecord(models.Model):
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE, related_name='references')
    snak = InheritanceForeignKey(Snak, on_delete=models.PROTECT)


class DataValue(Value):
    pass


class StringValue(DataValue):
    value = models.TextField()

    def __str__(self):
        return self.value


class UrlValue(DataValue):
    value = models.TextField()

    def __str__(self):
        return self.value


# Removed lower and upper bound, and created subclass with unit.
class QuantityValue(DataValue):
    number = models.FloatField()

    def __str__(self):
        return f"{self.number}"


class UnitQuantityValue(QuantityValue):
    unit = models.ForeignKey(Item, on_delete=models.PROTECT)


class TimeValue(DataValue):
    time = models.CharField(max_length=40)
    timezone = models.IntegerField()  # Offset from UTC in minutes
    # Precision for "before" and after "fields"
    precision = models.IntegerField(choices=(
        (0, 'Billion years'),
        (1, '100 million years'),
        (2, '10 million years'),
        (3, 'Million years'),
        (4, '100 thousand years'),
        (5, '10 thousand years'),
        (6, 'Thousand years'),
        (7, 'Century'),
        (8, 'Decade'),
        (9, 'Year'),
        (10, 'Month'),
        (11, 'Day'),
    ), blank=True, null=True)
    after = models.IntegerField(blank=True, null=True)
    before = models.IntegerField(blank=True, null=True)
    calendar_model = IriField()


class GlobeCoordinatesValue(DataValue):
    latitude = models.DecimalField(max_digits=11, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)
    precision = models.DecimalField(max_digits=12, decimal_places=9, validators=[positive])
    # Changed IRI to Item
    unit = models.ForeignKey(Item, on_delete=models.PROTECT)


class MultilingualTextValue(DataValue):
    pass


class MonolingualTextValue(DataValue):
    lang_code = models.CharField(max_length=3)
    value = models.TextField()
    multilingual_value = models.ForeignKey(MultilingualTextValue, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'({self.lang_code}) {self.value}'


class MultilingualMultiTextValue(DataValue):
    pass


class MonolingualMultiTextValue(DataValue):
    lang_code = models.CharField(max_length=3)
    values = models.TextField()  # FIXME
    multilingual_value = models.ForeignKey(MultilingualMultiTextValue, on_delete=models.CASCADE, blank=True, null=True)


class PropertyMapping(models.Model):
    """
    Maps symbolic keys to be used in code to the corresponding property.
    """
    key = models.CharField(max_length=255, unique=True)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, blank=True, null=True)


class ItemMapping(models.Model):
    """
    Maps symbolic keys to be used in code to the corresponding item.
    """
    key = models.CharField(max_length=255, unique=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)
