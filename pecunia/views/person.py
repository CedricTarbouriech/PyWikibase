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


class PersonCreation(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/person_form.html'
    form_class = PersonForm

    def form_valid(self, form):
        item = Item()
        item.save()
        item.add_value(PropertyMapping.get('is_a'), ItemMapping.get('person'))
        item.set_label('en', form.cleaned_data['title'])
        self.kwargs['display_id'] = item.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)


class PersonUpdate(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/index.html'


class PersonDelete(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/index.html'
