from django import forms
from django.contrib import admin

from wikibase.models import PropertyMapping, Datatype, Property
from .models import ItemMapping, Item


class ItemMappingForm(forms.ModelForm):
    class Meta:
        model = ItemMapping
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        used_items = ItemMapping.objects.values_list('item_id', flat=True)

        if self.instance and self.instance.pk:
            used_items = used_items.exclude(pk=self.instance.item_id)

        self.fields['item'].queryset = Item.objects.exclude(pk__in=used_items)


class PropertyMappingForm(forms.ModelForm):
    class Meta:
        model = PropertyMapping
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        used_properties = PropertyMapping.objects.values_list('property_id', flat=True)

        if self.instance and self.instance.pk:
            used_properties = used_properties.exclude(pk=self.instance.property_id)

        self.fields['property'].queryset = Property.objects.exclude(pk__in=used_properties)


@admin.register(PropertyMapping)
class PropertyMappingAdmin(admin.ModelAdmin):
    form = PropertyMappingForm
    list_display = ["key", "property"]
    search_fields = ["key", "property__display_id"]
    ordering = ["key"]


@admin.register(ItemMapping)
class ItemMappingAdmin(admin.ModelAdmin):
    form = ItemMappingForm
    list_display = ["key", "item"]
    search_fields = ["key", "item__display_id"]
    ordering = ["key"]


admin.site.register(Datatype)
