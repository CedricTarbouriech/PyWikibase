from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView

from pecunia.forms import DocumentForm
from pecunia.models import Document
from wikibase import models as m
from wikibase.models import PropertyMapping
from wikibase.views import InstanceDashboardView


class DocumentDashboard(InstanceDashboardView):
    template_name = 'pecunia/document_list.html'
    item_mapping_key = 'document'


class DocumentDisplay(TemplateView):
    template_name = 'pecunia/document_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            doc = Document.get_by_id(kwargs['display_id'])
        except ObjectDoesNotExist as e:
            raise Http404 from e

        context['document'] = doc
        return context


class DocumentCreation(LoginRequiredMixin, FormView):
    template_name = 'pecunia/document_form.html'
    form_class = DocumentForm

    def form_valid(self, form):
        document = Document()
        lang_code = 'en'
        title = m.MonolingualTextValue(language=lang_code,
                                       text=form.cleaned_data['title'])
        document.set_title(title)
        document.set_author(m.Item.objects.get(display_id=form.cleaned_data['author']))
        document.set_author_function(m.Item.objects.get(display_id=form.cleaned_data['author_function']))
        # date = m.TimeValue.create_from(value=form.cleaned_data['date'])
        # document.set_date(date)
        text = m.MonolingualTextValue(language=form.cleaned_data['language'], text=form.cleaned_data['text'])
        document.set_text(text)
        translation = m.MonolingualTextValue(language=form.cleaned_data['translation_language'],
                                             text=form.cleaned_data['translation'])
        document.set_translation(translation)
        document.set_provenance(m.Item.objects.get(display_id=form.cleaned_data['place']))
        document.save()
        self.kwargs['display_id'] = document.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)


class DocumentUpdate(LoginRequiredMixin, FormView):
    template_name = 'pecunia/document_form.html'
    form_class = DocumentForm

    def form_valid(self, form):
        display_id = self.kwargs['display_id']
        document = Document.get_by_id(display_id)
        document.set_text(form.cleaned_data['text'])
        document.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)

    def get_initial(self):
        document = m.Item.objects.get(display_id=self.kwargs['display_id'])
        text = document.get_value(PropertyMapping.get('text'))
        text_data = {}
        if text:
            text_data['language'] = text.language
            text_data['text'] = text.text
        # Préremplir les données du formulaire
        return {
            'title': document.get_value(PropertyMapping.get('title')),
            'date': document.get_value(PropertyMapping.get('date')),
        }.update(text_data)


class DocumentDelete(LoginRequiredMixin, TemplateView):
    template_name = 'wikibase/confirm_delete.html'
    success_url = reverse_lazy('document_list')

    def post(self, request, *args, **kwargs):
        if "confirm" in request.POST:
            m.Item.objects.get(display_id=self.kwargs['display_id']).delete()
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = f"Document {self.kwargs['display_id']}"
        return context
