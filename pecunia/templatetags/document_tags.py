from typing import re

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe

import wikibase.models as m
from wikibase.mapping import get_property_mapping

register = template.Library()


@register.filter
def line_numbers(document: m.Item) -> str:
    try:
        prop = get_property_mapping('text')
        if not prop:
            return f"Missing property mapping for key: {'text'}"
        statements = document.statement_set.filter(mainSnak__propertysnak__property=prop)

        max_n = max(map(int, re.findall('<lb n="(\d+)', statements[0].mainSnak.value.value)))
        output = ""
        for i in range(1, max_n + 1):
            output += f"<div>{i}</div>"

        return mark_safe(output)
    except ObjectDoesNotExist:
        return "-"



