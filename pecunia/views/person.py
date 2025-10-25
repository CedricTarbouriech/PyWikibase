from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic import TemplateView

from pecunia.models import Item
from .wikibase import InstanceDashboardView


class PersonDashboard(InstanceDashboardView):
    template_name = 'pecunia/person_list.html'
    item_mapping_key = 'person'


class PersonDisplay(TemplateView):
    template_name = 'pecunia/person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            person = Item.objects.get(display_id=kwargs['display_id'])
        except ObjectDoesNotExist as e:
            raise Http404 from e

        context['person'] = person
        return context
