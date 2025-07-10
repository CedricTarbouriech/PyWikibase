import re

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy, get_language
from lxml import etree

import wikibase.models as m
from wikibase.mapping import get_property_mapping

register = template.Library()


@register.filter
def label(value: m.DescribedEntity, lang_code: str) -> str:
    try:
        return value.labels.monolingualtextvalue_set.get(lang_code=lang_code).value
    except ObjectDoesNotExist:
        return gettext_lazy('no label')


@register.filter
def label_or_default(value: m.DescribedEntity, lang_code: str) -> str:
    try:
        return value.labels.monolingualtextvalue_set.get(lang_code=lang_code).value
    except ObjectDoesNotExist:
        try:
            return value.labels.monolingualtextvalue_set.get(lang_code='en')
        except ObjectDoesNotExist:
            return "-"


@register.filter
def description(value: m.DescribedEntity, lang_code: str) -> str:
    try:
        return value.descriptions.monolingualtextvalue_set.get(lang_code=lang_code).value or "-"
    except ObjectDoesNotExist:
        return gettext_lazy('-')


@register.filter
def description_or_default(value: m.DescribedEntity, lang_code: str) -> str:
    try:
        return value.descriptions.monolingualtextvalue_set.get(lang_code=lang_code).value or "-"
    except ObjectDoesNotExist:
        try:
            return value.descriptions.monolingualtextvalue_set.get(lang_code='en') or "-"
        except ObjectDoesNotExist:
            return "-"


@register.filter
def split(value: str, split_char: str) -> list[str]:
    return value.split(split_char)


@register.filter
def is_item(value: object) -> bool:
    return isinstance(value, m.Item)


@register.filter
def capitalize(s: str) -> str:
    return s.capitalize()


@register.filter
def prop(item: object, prop_key_mapping: str) -> str:
    prop = get_property_mapping(prop_key_mapping)
    if not prop:
        return f"Missing property mapping for key: {prop_key_mapping}"
    statements = item.statement_set.filter(mainSnak__propertysnak__property=prop)
    if statements:
        statement = statements[0].mainSnak.value
        if isinstance(statement, m.Item):
            return label_or_default(statement, translation.get_language())
        return statements[0].mainSnak.value
    return "-"


@register.filter
def prop_mtv_value(item: object, prop_key_mapping: str) -> str:
    try:
        prop = get_property_mapping(prop_key_mapping)
        if not prop:
            return f"Missing property mapping for key: {prop_key_mapping}"
        statements = item.statement_set.filter(mainSnak__propertysnak__property=prop)
        return statements[0].mainSnak.value.value
    except ObjectDoesNotExist:
        return "-"


@register.filter
def prop_label(item: object, prop_key_mapping: str) -> str:
    try:
        prop = get_property_mapping(prop_key_mapping)
        if not prop:
            return f"Missing property mapping for key: {prop_key_mapping}"
        return prop.labels.monolingualtextvalue_set.get(lang_code=translation.get_language()).value
    except ObjectDoesNotExist:
        try:
            return prop.labels.monolingualtextvalue_set.get(lang_code="en").value
        except ObjectDoesNotExist:
            return "-"


def handle_tag(el: etree._Element) -> str:
    # print(
    #     f"appel de handle_tag avec tag={el.tag}, attribs={el.attrib}, text={el.text}, tail='{el.tail}', children={el.getchildren()}")
    output = ""
    inner = ""
    for child in el.getchildren():
        # print(el, child)
        inner += handle_tag(child)
    text = el.text or ''
    if el.tag == 'w':
        w_text = text or inner
        w_type = el.get("type", "")
        w_id = el.get("id", "")
        if w_id:
            output += f'<a class="tagged-element {"typed type-" + w_type if w_type else ""}" href="/item/{w_id}">{w_text}</a>'
        else:
            output += f'<span class="tagged-element {"typed type-" + w_type if w_type else ""}">{w_text}</span>'
    elif el.tag == 'lb' and int(el.attrib['n']) != 0:
        output += '<br>'
    elif el.tag == 'orig':
        w_text = text.strip() + inner
        output += w_text.upper()
    elif el.tag == 'unclear':
        w_text = text.strip()
        w_text = ''.join(c + ("\u0323" if not c.isspace() else "") for c in w_text)
        output += w_text + inner
    elif el.tag == 'supplied':
        w_text = text.strip() or ''
        output += f"[{w_text}]"
    elif el.tag == 'g':
        output += f"(({el.attrib['type']}))"
    elif el.text:
        output += str(text).strip()

    # Ajouter le texte qui suit la balise <w>
    if el.tail:
        output += el.tail.strip()
    return output


@register.filter
def highlight_words(value):
    if not value:
        return ''
    value = value.replace('\r\n', ' ')
    root = etree.fromstring(f"<xml>{value}</xml>")

    # Conteneur HTML
    output = ""
    if root.line_numbers:
        output += root.line_numbers

    for el in root:
        output += handle_tag(el)

    return mark_safe(output)


@register.filter
def generate_div_for_lb(value):
    max_n = max(map(int, re.findall('<lb n="(\d+)', value)))
    output = ""
    for i in range(1, max_n + 1):
        output += f"<div>{i}</div>"

    return mark_safe(output)


@register.filter
def snak_type(snak: m.Snak) -> int:
    if isinstance(snak, m.PropertyValueSnak):
        return 0
    elif isinstance(snak, m.PropertySomeValueSnak):
        return 1
    elif isinstance(snak, m.PropertyNoValueSnak):
        return 2


@register.filter
def html(value: m.Value) -> str:
    if isinstance(value, m.Item):
        return mark_safe(f"<a href='{reverse('item_display', args=[value.display_id])}'>{label_or_default(value, get_language())}</a>")
    elif isinstance(value, m.UrlValue):
        return mark_safe(f"<a href='{value.value}'>{value.value}</a>")
    else:
        return mark_safe(value)
