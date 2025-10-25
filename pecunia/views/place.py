from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .wikibase import InstanceDashboardView


class PlaceDashboard(InstanceDashboardView):
    template_name = 'pecunia/place_list.html'
    item_mapping_key = 'place'


class PlaceDisplay(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/index.html'
