import wikibase.models as m
from wikibase.models import DescribedEntity


def create_item() -> m.Item:
    """
    Create and save an item
    :return: the newly created item
    """
    item = m.Item()
    item.save()
    return item


def get_item(**kwargs) -> m.Item:
    return m.Item.objects.get(**kwargs)


def get_items() -> list[m.Item]:
    return list(m.Item.objects.all())


def create_property(datatype: m.Datatype) -> m.Property:
    prop = m.Property(data_type=datatype)
    prop.save()
    return prop


def add_value_property(subject: DescribedEntity, prop: m.Property, value: m.Value, rank: int = 0) -> m.Statement:
    """
    Adds a statement composed of a property, a value and a rank to a subject.
    :param subject: 
    :param prop: 
    :param value: 
    :param rank: 
    :return: 
    """
    assert isinstance(subject, (m.Item, m.Property))
    assert value.__class__ is prop.data_type.type
    snak = m.PropertyValueSnak(property=prop, value=value)
    snak.save()
    statement = m.Statement(subject=subject, mainSnak=snak, rank=rank)
    statement.clean_fields()
    statement.save()
    return statement


def add_label(subject: DescribedEntity, lang_code: str, label: str) -> None:
    """
    Adds a label to a subject. Replace the label if already existing.
    :param subject:
    :param lang_code:
    :param label:
    :return:
    """
    if subject.labels.monolingualtextvalue_set.filter(lang_code=lang_code).exists():
        mtv = subject.labels.monolingualtextvalue_set.get(lang_code=lang_code)
        mtv.value = label
        mtv.save()
    else:
        m.MonolingualTextValue.objects.create(lang_code=lang_code, value=label, multilingual_value=subject.labels)


def add_description(subject: DescribedEntity, lang_code: str, description: str) -> None:
    if subject.descriptions.monolingualtextvalue_set.filter(lang_code=lang_code).exists():
        mtv = subject.descriptions.monolingualtextvalue_set.get(lang_code=lang_code)
        mtv.value = description
        mtv.save()
    else:
        m.MonolingualTextValue.objects.create(lang_code=lang_code, value=description,
                                              multilingual_value=subject.descriptions)


def get_value_property(item: object, prop: object) -> bool:
    statements = item.statement_set.filter(mainSnak__propertysnak__property=prop)
    return statements[0].mainSnak.value if statements else None


def set_value_property(item, prop, value):
    statement = item.statement_set.filter(mainSnak__propertysnak__property=prop)
    if statement:
        statement[0].mainSnak = value
