import re

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.utils.safestring import mark_safe

import wikibase.models as m
from wikibase.models import PropertyMapping

register = template.Library()


@register.filter
def line_numbers(document: m.Item) -> str:
    try:
        prop = PropertyMapping.get('text')
        if not prop:
            return f"Missing property mapping for key: {'text'}"
        statements = document.statements.filter(mainsnak__property=prop)

        l = list(map(int, re.findall('<lb n="(\d+)', statements[0].mainsnak.value.text)))
        max_n = 1
        if l:
            max_n = max(l)
        output = ""
        for i in range(1, max_n + 1):
            output += f"<div>{i}</div>"

        return mark_safe(output)
    except ObjectDoesNotExist:
        return "-"
