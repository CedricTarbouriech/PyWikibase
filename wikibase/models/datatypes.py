from django.core import exceptions
from django.core.exceptions import ValidationError
from django.db import models

from .base import Value, Item, Property, DescribedEntity, Entity


def positive(v: float | int) -> None:
    if v < 0:
        raise exceptions.ValidationError(f'expected v >= 0, got {v}', 'positive')


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
        return globals()[self.class_name]  # FIXME: If Property is not imported, it doesn’t wo

    def __str__(self):
        return f'Datatype[{self.class_name}]'

    def __repr__(self):
        return f'Datatype[{self.class_name}]'


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
    lower = models.FloatField(blank=True, null=True)
    upper = models.FloatField(blank=True, null=True)
    unit = models.ForeignKey(Item, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"{self.number}"


class TimeValue(DataValue):
    time = models.CharField(max_length=40)  # +YYYY-MM-DDThh:mm:ssZ
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
        (12, 'Hour'),
        (13, 'Minute'),
        (14, 'Second'),
    ), blank=True, null=True)
    after = models.IntegerField(blank=True, null=True)
    before = models.IntegerField(blank=True, null=True)
    calendar_model = models.ForeignKey(Item, on_delete=models.PROTECT)


class GlobeCoordinatesValue(DataValue):
    latitude = models.DecimalField(max_digits=11, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)
    precision = models.DecimalField(max_digits=12, decimal_places=9, validators=[positive])
    # Changed IRI to Item
    globe = models.ForeignKey(Item, on_delete=models.PROTECT)


class MonolingualTextValue(DataValue):
    language = models.CharField(max_length=3)
    text = models.TextField()

    def __str__(self):
        return f'({self.language}) {self.text}'


class Label(MonolingualTextValue):
    described_entity = models.ForeignKey(DescribedEntity, related_name='labels', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if Label.objects.exclude(pk=self.pk).filter(
                described_entity=self.described_entity,
                language=self.language
        ).exists():
            raise ValidationError("A label is already defined for this entity")


class Description(MonolingualTextValue):
    described_entity = models.ForeignKey(DescribedEntity, related_name='descriptions', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if Description.objects.exclude(pk=self.pk).filter(
                described_entity=self.described_entity,
                language=self.language
        ).exists():
            raise ValidationError("A description is already defined for this entity")


class Alias(MonolingualTextValue):
    described_entity = models.ForeignKey(DescribedEntity, related_name='aliases', on_delete=models.CASCADE)
