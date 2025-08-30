from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView

from pecunia.forms import DocumentMetadataForm, DocumentTextForm
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

        processes = []

        context['document'] = doc
        context['processes'] = processes
        return context


class DocumentCreation(LoginRequiredMixin, FormView):
    template_name = 'pecunia/document_form.html'
    form_class = DocumentMetadataForm

    def form_valid(self, form):
        with transaction.atomic():
            document = Document.objects.create()
            print(form.cleaned_data)
            document.set_label(form.cleaned_data['title_language'], form.cleaned_data['title'])
            title = m.MonolingualTextValue(language=form.cleaned_data['title_language'],
                                           text=form.cleaned_data['title'])
            title.save()
            document.set_title(title)
            document.set_source_type(m.Item.objects.get(display_id=form.cleaned_data['source_type']))
            document.set_author(m.Item.objects.get(display_id=form.cleaned_data['author']))
            document.set_author_function(m.Item.objects.get(display_id=form.cleaned_data['author_function']))
            document.set_provenance(m.Item.objects.get(display_id=form.cleaned_data['place']))
            print(form.cleaned_data)
            print(self.kwargs)
            print(document.get_value(PropertyMapping.get('text')))
            document.save()
            print(document.statements)
            self.kwargs['display_id'] = document.display_id
            print(document.get_value(PropertyMapping.get('text')))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)


class DocumentUpdateMetadata(LoginRequiredMixin, FormView):
    template_name = 'pecunia/document_form.html'
    form_class = DocumentMetadataForm

    def form_valid(self, form):
        with transaction.atomic():
            display_id = self.kwargs['display_id']
            document = Document.get_by_id(display_id)
            title = document.get_title()
            title.language = form.cleaned_data['title_language']
            title.text = form.cleaned_data['title']
            title.save()
            document.set_source_type(m.Item.objects.get(display_id=form.cleaned_data['source_type']))
            document.set_author(m.Item.objects.get(display_id=form.cleaned_data['author']))
            document.set_author_function(m.Item.objects.get(display_id=form.cleaned_data['author_function']))
            document.set_provenance(m.Item.objects.get(display_id=form.cleaned_data['place']))
            document.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        document = m.Item.objects.get(display_id=self.kwargs['display_id'])
        kwargs["initial"] = {
            'title': document.get_value(PropertyMapping.get('title')).text,
            'title_language': document.get_value(PropertyMapping.get('title')).language,
            'source_type': document.get_value(PropertyMapping.get('source_type')).display_id,
            'author': document.get_value(PropertyMapping.get('author')).display_id,
            'author_function': document.get_value(PropertyMapping.get('author_function')).display_id,
            'place': document.get_value(PropertyMapping.get('provenance')).display_id,
        }
        return kwargs


class DocumentUpdateText(LoginRequiredMixin, FormView):
    template_name = 'pecunia/document_annotator.html'
    form_class = DocumentTextForm

    def form_valid(self, form):
        display_id = self.kwargs['display_id']
        document = Document.get_by_id(display_id)
        text = document.get_value(PropertyMapping.get('text'))
        with transaction.atomic():
            if text:
                text.language = form.cleaned_data['language']
                text.text = form.cleaned_data['text']
                text.save()
            else:
                text = m.MonolingualTextValue(language=form.cleaned_data['language'], text=form.cleaned_data['text'])
                text.save()
                document.set_text(text)
            document.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        document = m.Item.objects.get(display_id=self.kwargs['display_id'])
        if document.get_value(PropertyMapping.get('text')):
            kwargs["initial"] = {
                'text': document.get_value(PropertyMapping.get('text')).text,
                'language': document.get_value(PropertyMapping.get('text')).language
            }
        return kwargs


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
