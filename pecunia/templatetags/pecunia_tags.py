import re

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils import translation
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy, get_language
from lxml import etree

import wikibase.models as m
from wikibase.models import PropertyMapping, PropertySnak

register = template.Library()

DEFAULT_LANGUAGE = 'en'


@register.filter
def label(described_entity: m.DescribedEntity, lang_code: str) -> str:
    """
    Returns the label in the given of the given described_entity.
    If the label does not exist, returns the pretty display_id.
    :param described_entity: the DescribedEntity instance from which the label is obtained
    :param lang_code: the language code of the label
    :return: the label in the given language code
    """
    try:
        return described_entity.labels.get(language=lang_code).text
    except ObjectDoesNotExist:
        return described_entity.pretty_display_id


@register.filter
def label_or_default(described_entity: m.DescribedEntity, lang_code: str) -> str:
    try:
        return described_entity.labels.get(language=lang_code).text
    except ObjectDoesNotExist:
        try:
            return described_entity.labels.get(language=DEFAULT_LANGUAGE)
        except ObjectDoesNotExist:
            return described_entity.pretty_display_id


@register.filter
def description(value: m.DescribedEntity, lang_code: str) -> str:
    try:
        return value.descriptions.get(language=lang_code).text or "-"
    except ObjectDoesNotExist:
        return gettext_lazy('-')


@register.filter
def description_or_default(value: m.DescribedEntity, lang_code: str) -> str:
    try:
        return value.descriptions.get(language=lang_code).text or "-"
    except ObjectDoesNotExist:
        try:
            return value.descriptions.get(language='en') or "-"
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
def prop(item: object, prop_key_mapping: str) -> PropertySnak | str:
    prop = PropertyMapping.get(prop_key_mapping)
    if not prop:
        return f"Missing property mapping for key: {prop_key_mapping}"
    statements = item.statements.filter(mainsnak__property=prop)
    if statements:
        return statements[0].mainsnak
    return "-"


@register.filter
def prop_list(item: object, prop_key_mapping: str) -> str:
    prop = PropertyMapping.get(prop_key_mapping)
    if not prop:
        return f"Missing property mapping for key: {prop_key_mapping}"
    statements = item.statements.filter(mainsnak__property=prop)
    if statements:
        return ", ".join(html(statement.mainsnak) for statement in statements)
    return "-"


@register.filter
def prop_mtv_value(item: m.Entity, prop_key_mapping: str) -> str:
    try:
        prop = PropertyMapping.get(prop_key_mapping)
        if not prop:
            return f"Missing property mapping for key: {prop_key_mapping}"
        statements = item.statements.filter(mainsnak__property=prop)
        return statements[0].mainsnak.value.text
    except ObjectDoesNotExist:
        return "-"


@register.filter
def prop_mtv_langage(item: m.Entity, prop_key_mapping: str) -> str:
    try:
        prop = PropertyMapping.get(prop_key_mapping)
        if not prop:
            return f"Missing property mapping for key: {prop_key_mapping}"
        statements = item.statements.filter(mainsnak__property=prop)
        return statements[0].mainsnak.value.language
    except ObjectDoesNotExist:
        return "-"


@register.filter
def prop_label(item: object, prop_key_mapping: str) -> str:
    try:
        prop = PropertyMapping.get(prop_key_mapping)
        if not prop:
            return f"Missing property mapping for key: {prop_key_mapping}"
        return prop.labels.get(language=translation.get_language()).text
    except ObjectDoesNotExist:
        try:
            return prop.labels.get(language="en").text
        except ObjectDoesNotExist:
            return "-"


def handle_tag(el: etree._Element) -> str:
    output = ""
    inner = ""
    for child in el.getchildren():
        inner += handle_tag(child)
    text = (el.text or '') + inner
    if el.tag == 'w' and not el.get("part", None):
        w_text = text
        w_type = el.get("type", "")
        w_id = el.get("qid", "")
        if w_id:
            output += f'<a class="tagged-element {"typed type-" + w_type if w_type else ""}" href="/item/{w_id}">{w_text}</a>'
        else:
            output += f'<span class="tagged-element {"typed type-" + w_type if w_type else ""}">{w_text}</span>'
    elif el.tag == 'lb' and int(el.attrib['n']) != 0:
        if 'break' in el.attrib and el.attrib['break'] == "no" or 'type' in el.attrib and el.attrib[
            'type'] == "worddiv":
            output += '-'
        output += '<br>'
    elif el.tag == 'orig':
        w_text = text
        output += w_text.upper()
    elif el.tag == 'unclear':
        w_text = text
        w_text = ''.join(c + ("\u0323" if not c.isspace() else "") for c in w_text)
        output += w_text
    elif el.tag == 'gap':
        # if 'extent' in el.attrib and el.attrib['extent'] == 'unknown' and el.attrib['reason'] == 'lost':
        #     output += ""
        # else:
        res = ''
        if 'quantity' in el.attrib:
            character_number = int(el.attrib['quantity'])
            res = "." * character_number
        elif 'extent' in el.attrib:
            res = "----"
        if el.attrib['reason'] == 'lost':
            res = f"[{res}]"
        output += res
    elif el.tag == 'del':
        res = text
        if res[0] == '[' and res[-1] == ']':
            res = res[1:-1]
        output += f"〚{res}〛"
    elif el.tag == 'supplied':
        reason = el.attrib['reason']
        if reason == 'lost':
            output += f"[{text}]"
        elif reason == 'omitted':
            output += f"&#60;{text}&#62;"
    elif el.tag == 'surplus':
        output += f"{{{text}}}"
    elif el.tag == 'choice':
        output += f"&#60;{text}&#62;"
    elif el.tag == 'sic':
        return ""
    elif el.tag == 'expan':
        output += f"{text}"
    elif el.tag == 'ex':
        final = ")"
        if 'cert' in el.attrib and el.attrib['cert'] == 'low':
            final = "?)"
        output += f"({text}{final}"
    elif el.tag == 'space':
        output += 'v.'
    elif el.tag == 'g':
        output += f"(({el.attrib['type']}))"
    elif el.text:
        output += str(text)

    if inner:
        output += str(inner)

    # Ajouter le texte qui suit la balise <w>
    if el.tail:
        output += el.tail
    return output


@register.filter
def highlight_words(value):
    if not value:
        return ''
    root = etree.fromstring(f"<xml>{value}</xml>")

    # Conteneur HTML
    output = ""
    if root.text:
        output += root.text

    for el in root:
        output += handle_tag(el)
    # Remove first <br>
    if output.startswith('<br>'):
        output = output[4:]
    output = output.replace('\n', '')
    output = re.sub(r'](\s*)\[', r'\1', output)
    return mark_safe(output)


@register.filter
def generate_div_for_lb(value):
    max_n = max(map(int, re.findall('<lb n="(\d+)', value)))
    output = ""
    for i in range(1, max_n + 1):
        output += f"<div>{i}</div>"

    return mark_safe(output)


@register.filter
def has_prop(value: m.Entity, prop_key: str) -> bool:
    return value.statements.filter(mainsnak__property=PropertyMapping.get(prop_key)).count() != 0


@register.filter
def html(snak: m.PropertySnak | str) -> str:
    if isinstance(snak, str):
        return mark_safe(snak)
    if isinstance(snak.value, m.Item):
        return mark_safe(
            f"<a href='{reverse('item_display', args=[snak.value.display_id])}'>{label_or_default(snak.value, get_language())}</a>")
    elif isinstance(snak.value, m.UrlValue):
        label = snak.value.value
        if snak.used_in_statement.qualifiers.filter(snak__property=PropertyMapping.get('url_label')).count() > 0:
            qualifier = snak.used_in_statement.qualifiers.filter(snak__property=PropertyMapping.get('url_label'))[0]
            label = qualifier.snak.value.value
        return mark_safe(f"<a href='{snak.value.value}'>{label}</a>")
    elif isinstance(snak.value, m.GlobeCoordinatesValue):
        return mark_safe(
            f"<span>{snak.value.latitude}, {snak.value.longitude}"
            f"<div id='map-{snak.value.id}' class='map' "
            f"data-lat='{snak.value.latitude}' data-lon='{snak.value.longitude}'></div></span>"
        )
    else:
        return mark_safe(snak.value)

# FIXME retirer cette fonction
@register.filter
def html2(snak: m.PropertySnak | str) -> str:
    if isinstance(snak, str):
        return mark_safe(snak)
    if isinstance(snak.value, m.Item):
        return mark_safe(
            f"<a href='{reverse('item_display', args=[snak.value.display_id])}'>{label_or_default(snak.value, get_language())}</a>")
    elif isinstance(snak.value, m.UrlValue):
        label = snak.value.value
        return mark_safe(f"<a href='{snak.value.value}'>{label}</a>")
    elif isinstance(snak.value, m.GlobeCoordinatesValue):
        return mark_safe(
            f"<span>{snak.value.latitude}, {snak.value.longitude}"
            f"<div id='map-{snak.value.id}' class='map' "
            f"data-lat='{snak.value.latitude}' data-lon='{snak.value.longitude}'></div></span>"
        )
    else:
        return mark_safe(snak.value)