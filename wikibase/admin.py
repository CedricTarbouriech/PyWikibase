from django.contrib import admin

from wikibase.models import PropertyMapping, ItemMapping, Datatype


# Register your models here.
@admin.register(PropertyMapping)
class PropertyMappingAdmin(admin.ModelAdmin):
    list_display = ["key", "property"]
    search_fields = ["key", "property__display_id"]
    ordering = ["key"]


@admin.register(ItemMapping)
class ItemMappingAdmin(admin.ModelAdmin):
    list_display = ["key", "item"]
    search_fields = ["key", "item__display_id"]
    ordering = ["key"]


admin.site.register(Datatype)
