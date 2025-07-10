from django.http import Http404
from django.views.generic import TemplateView

from wikibase import models as m
from wikibase.mapping import get_item_mapping, get_property_mapping


class InstanceDashboardView(TemplateView):
    item_mapping_key = None

    def dispatch(self, request, *args, **kwargs):
        if not get_item_mapping(self.item_mapping_key):
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        items = m.Item.objects.all()
        result = []
        is_a_prop = get_property_mapping('is_a')
        for item in items:
            if not item.statement_set.exists():
                continue
            if item.statement_set.filter(mainSnak__propertysnak__property=is_a_prop,
                                         mainSnak__propertysnak__propertyvaluesnak__value=get_item_mapping(
                                             self.item_mapping_key)).exists():
                result.append(item)

        context['items'] = result
        return context
