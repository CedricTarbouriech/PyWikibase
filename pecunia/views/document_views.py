from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView

import pecunia.models_utils as mutils
from pecunia.forms import DocumentForm
from pecunia.views.abstract import InstanceDashboardView
from wikibase import models as m, api as wbapi
from wikibase.mapping import get_property_mapping


class DocumentDashboard(InstanceDashboardView):
    template_name = 'pecunia/document_list.html'
    item_mapping_key = 'document'


class DocumentDisplay(TemplateView):
    template_name = 'pecunia/document_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            doc = mutils.get_document_by_id(kwargs['display_id'])
        except ObjectDoesNotExist as e:
            raise Http404 from e

        context['document'] = doc
        return context


class DocumentCreation(LoginRequiredMixin, FormView):
    template_name = 'pecunia/document_form.html'
    form_class = DocumentForm

    def form_valid(self, form):
        lang_code = 'en'
        title = form.cleaned_data['title']
        document = mutils.create_document(lang_code, title)
        document = mutils.set_author(document, m.Item.objects.get(display_id=form.cleaned_data['author']))
        wbapi.add_value_property(document, get_property_mapping('author_function'),
                                 m.Item.objects.get(display_id=form.cleaned_data['author_function']))
        date = m.StringValue(value=form.cleaned_data['date'])
        date.save()
        wbapi.add_value_property(document, get_property_mapping('date'), date)
        text = m.MonolingualTextValue(lang_code=form.cleaned_data['language'], value=form.cleaned_data['text'])
        text.save()
        wbapi.add_value_property(document, get_property_mapping('text'), text)
        translation = m.MonolingualTextValue(lang_code=form.cleaned_data['translation_language'],
                                             value=form.cleaned_data['translation'])
        translation.save()
        wbapi.add_value_property(document, get_property_mapping('translation'), translation)
        wbapi.add_value_property(document, get_property_mapping('provenance'),
                                 m.Item.objects.get(display_id=form.cleaned_data['place']))

        self.kwargs['display_id'] = document.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)


class DocumentUpdate(LoginRequiredMixin, FormView):
    template_name = 'pecunia/document_form.html'
    form_class = DocumentForm

    def form_valid(self, form):
        display_id = self.kwargs['display_id']
        document = mutils.get_document_by_id(display_id)
        document = mutils.set_text(document, form.cleaned_data['text'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)

    def get_initial(self):
        document = m.Item.objects.get(display_id=self.kwargs['display_id'])
        # Préremplir les données du formulaire
        return {
            'title': wbapi.get_value_property(document, get_property_mapping('title')),
            'date': wbapi.get_value_property(document, get_property_mapping('date')),
            'language': wbapi.get_value_property(document, get_property_mapping('text')).lang_code,
            'text': wbapi.get_value_property(document, get_property_mapping('text')).value,
        }


class DocumentDelete(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/confirm_delete.html'
    success_url = reverse_lazy('document_list')

    def post(self, request, *args, **kwargs):
        if "confirm" in request.POST:
            m.Item.objects.get(display_id=self.kwargs['display_id']).delete()
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = f"Document {self.kwargs['display_id']}"
        return context
