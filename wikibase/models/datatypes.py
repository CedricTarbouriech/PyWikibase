from django.core import exceptions
from django.core.exceptions import ValidationError
from django.db import models

from .base import Value, Item, DescribedEntity


def positive(v: float | int) -> None:
    if v < 0:
        raise exceptions.ValidationError(f'expected v >= 0, got {v}', 'positive')


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
    calendar_model = models.ForeignKey(Item, on_delete=models.PROTECT)


class GlobeCoordinatesValue(DataValue):
    latitude = models.DecimalField(max_digits=11, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)
    precision = models.DecimalField(max_digits=12, decimal_places=9, validators=[positive])
    # Changed IRI to Item
    unit = models.ForeignKey(Item, on_delete=models.PROTECT)


class MonolingualTextValue(DataValue):
    lang_code = models.CharField(max_length=3)
    value = models.TextField()

    def __str__(self):
        return f'({self.lang_code}) {self.value}'


class Label(MonolingualTextValue):
    described_entity = models.ForeignKey(DescribedEntity, related_name='labels', on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if Label.objects.exclude(pk=self.pk).filter(
                described_entity=self.described_entity,
                lang_code=self.lang_code
        ).exists():
            raise ValidationError("A label is already defined for this entity")


class Description(MonolingualTextValue):
    described_entity = models.ForeignKey(DescribedEntity, related_name='descriptions', on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if Description.objects.exclude(pk=self.pk).filter(
                described_entity=self.described_entity,
                lang_code=self.lang_code
        ).exists():
            raise ValidationError("A description is already defined for this entity")


class Alias(MonolingualTextValue):
    described_entity = models.ForeignKey(DescribedEntity, related_name='aliases', on_delete=models.PROTECT)
