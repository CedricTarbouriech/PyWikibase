from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase
from django import forms
from django.contrib import admin

from .models import PropertyMapping, Datatype, Property, ItemMapping, Item, PropertyOrderPreference


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


class PropertyOrderPreferenceAdminProxy(Item):
    class Meta:
        proxy = True
        verbose_name = "Property order list"
        verbose_name_plural = "Property order lists"


class ItemPropertyInline(SortableInlineAdminMixin, admin.TabularInline):
    model = PropertyOrderPreference
    extra = 1
    fields = ('prop', 'ordering')
    verbose_name = "Propriété de l’Item"
    verbose_name_plural = "Propriétés de l’Item"


@admin.register(PropertyOrderPreferenceAdminProxy)
class ItemAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [ItemPropertyInline]
    ordering = ['display_id']
    list_display = ('display_name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Ne garder que les Items ayant au moins une ItemProperty
        return qs.filter(itemproperty__isnull=False).distinct()

    def display_name(self, obj):
        return str(obj)

    display_name.short_description = "Item"

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = "Gestion des Propriétés de l’Item"
        return super().changeform_view(request, object_id, form_url, extra_context)
