import wikibase.models as m


def get_item_mapping(key: str) -> m.Item | None:
    try:
        return m.ItemMapping.objects.get(key=key).item
    except m.ItemMapping.DoesNotExist:
        return None


def get_property_mapping(key: str) -> m.Property | None:
    try:
        return m.PropertyMapping.objects.get(key=key).property
    except m.PropertyMapping.DoesNotExist:
        return None
