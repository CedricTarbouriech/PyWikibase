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



class IriField(models.TextField):
    pass


class Value(models.Model):
    objects = InheritanceManager()


class Entity(Value):
    pass

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
    def get_labels(self):
        return self.labels.monolingualtextvalue_set.all()

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
