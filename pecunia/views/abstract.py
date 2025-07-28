from django.http import Http404
from django.views.generic import TemplateView

from wikibase import models as m
from wikibase.models import ItemMapping, PropertyMapping


class InstanceDashboardView(TemplateView):
    item_mapping_key = None

    def dispatch(self, request, *args, **kwargs):
        if not ItemMapping.has(self.item_mapping_key):
            raise Http404(f"Item mapping '{self.item_mapping_key}' does not exist.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        items = m.Item.objects.all()
        result = []
        is_a_prop = PropertyMapping.get('is_a')
        item_mapping = ItemMapping.get(self.item_mapping_key)
        for item in items:
            if not item.statements.exists():
                continue
            if item.statements.filter(mainsnak__property=is_a_prop,
                                      mainsnak__value=item_mapping).exists():
                result.append(item)

        context['items'] = result
        return context
