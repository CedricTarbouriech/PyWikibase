from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from pecunia.forms import PersonForm
from pecunia.models import ItemMapping, PropertyMapping, Item
from .wikibase import InstanceDashboardView


class PersonDashboard(InstanceDashboardView):
    template_name = 'pecunia/person_list.html'
    item_mapping_key = 'person'


class PersonDisplay(TemplateView):
    template_name = 'pecunia/index.html'