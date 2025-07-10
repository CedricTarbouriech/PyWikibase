from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from pecunia.forms import PersonForm
from pecunia.views.abstract import InstanceDashboardView
from wikibase import api as wbapi
from wikibase.mapping import get_item_mapping, get_property_mapping


class PersonDashboard(InstanceDashboardView):
    template_name = 'pecunia/person_list.html'
    item_mapping_key = 'person'


class PersonDisplay(TemplateView):
    template_name = 'pecunia/index.html'


class PersonCreation(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/person_form.html'
    form_class = PersonForm

    def form_valid(self, form):
        item = wbapi.create_item()
        wbapi.add_value_property(item, get_property_mapping('is_a'), get_item_mapping('person'))
        wbapi.add_label(item, 'en', form.cleaned_data['title'])
        self.kwargs['display_id'] = item.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)


class PersonUpdate(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/index.html'


class PersonDelete(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/index.html'
