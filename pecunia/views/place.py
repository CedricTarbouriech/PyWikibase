from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic import TemplateView

from .wikibase import InstanceDashboardView
from ..models import Item


class PlaceDashboard(InstanceDashboardView):
    template_name = 'pecunia/place_list.html'
    item_mapping_key = 'place'


class PlaceDisplay(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/place_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            place = Item.objects.get(display_id=kwargs['display_id'])
        except ObjectDoesNotExist as e:
            raise Http404 from e

        context['place'] = place
        return context
