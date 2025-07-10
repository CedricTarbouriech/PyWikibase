from wikibase import api as wbapi, models as m
from wikibase.mapping import get_item_mapping, get_property_mapping


def get_documents():
    """
    Returns a queryset of items classified as documents.
    :return: Queryset of items classified as documents.
    """
    return m.Item.objects.filter(statement__mainSnak__propertysnak__property=get_property_mapping('is_a'),
                                 statement__mainSnak__propertysnak__propertyvaluesnak__value=get_item_mapping(
                                     'document'))


def get_document_by_id(display_id: int) -> m.Item:
    return get_documents().get(display_id=display_id)


def create_document(lang_code, title):
    item = wbapi.create_item()
    wbapi.add_label(item, lang_code, title)
    wbapi.add_value_property(item, get_property_mapping('is_a'), get_item_mapping('document'))
    mtv = m.MonolingualTextValue(lang_code=lang_code, value=title)
    mtv.save()
    wbapi.add_value_property(item, get_property_mapping('document_title'), mtv)
    return item


def set_author(document, author):
    wbapi.set_value_property(document, get_property_mapping('author'), author)
    return document


def set_text(document, text):
    statement = document.statement_set.get(mainSnak__propertysnak__property=get_property_mapping('text'))
    statement.mainSnak.value.value = text
    statement.mainSnak.value.save()
