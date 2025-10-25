import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView

from pecunia.forms import DocumentMetadataForm, DocumentTextForm
from pecunia.models import Document
import pecunia.models as m
from pecunia.models import PropertyMapping
from .wikibase import InstanceDashboardView
from .api import json_to_python


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
        if document.get_value(PropertyMapping.get('language')):
            document.set_value(PropertyMapping.get('language'), form.cleaned_data['language'])
        else:
            # FIXME
            # document.add_value(PropertyMapping.get('language'), form.cleaned_data['language'])
            pass
        document.set_value(PropertyMapping.get('text'), m.StringValue.objects.create(value=form.cleaned_data['text']))
        document.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.kwargs['display_id']
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        document = m.Item.objects.get(display_id=self.kwargs['display_id'])
        if document.get_value(PropertyMapping.get('text')):
            kwargs["initial"] = {
                'text': document.get_value(PropertyMapping.get('text')),
                'language': document.get_value(PropertyMapping.get('language'))
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


class AnnotatorApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        document = Document.get_by_id(data['document'])
        print(document)

        entities = data['entities']

        tokens = {}
        for token in entities['taggedEntities'].values():
            tokens[token['tokenId']] = token
        for token in entities['untaggedEntities'].values():
            tokens[token['tokenId']] = token

        reconciliations = data['reconciliations']
        items = {}
        unknown_entities = []
        for new_entity in reconciliations['newEntities']:
            items[new_entity['tokenId']] = m.Item.objects.create()

        for unknown_entity in reconciliations['unknownEntities']:
            unknown_entities.append(unknown_entity['tokenId'])

        for linked_entity in reconciliations['linkedEntities']:
            items[linked_entity['token']['tokenId']] = m.Item.objects.get(display_id=linked_entity['qid'])

        schemata = data['schemata']
        for schema in schemata:
            token = schema['token']
            item = items[token['tokenId']]

            for term in schema['terms']:
                if term['type'] == 'label':
                    item.set_label(term['langCode'], term['value'])
                if term['type'] == 'description':
                    item.set_description(term['langCode'], term['value'])
                if term['type'] == 'alias':
                    pass  # TODO Implement

            for json_statement in schema['statements']:
                prop = m.Property.objects.get(display_id=json_statement['property'])

                for snak in json_statement['statements']:
                    json_snaktype = snak['mainSnak']['type']
                    json_value = snak['mainSnak']['value']

                    mainsnak = m.PropertySnak(property=prop)
                    print(f"snak {snak}")
                    if json_snaktype == 'Item':
                        if snak['mainSnak']['value']['item']['tokenId'] in unknown_entities:
                            mainsnak.type = m.PropertySnak.Type.SOME_VALUE
                        else:
                            mainsnak.type = m.PropertySnak.Type.VALUE
                            mainsnak.value = items[snak['mainSnak']['value']['item']['tokenId']]
                    else:
                        mainsnak.type = m.PropertySnak.Type.VALUE
                        mainsnak.value = json_to_python(json_snaktype, json_value)
                    mainsnak.save()
                    statement = m.Statement(subject=item, mainsnak=mainsnak, rank=0)
                    statement.save()

                    for json_qualifier in snak['qualifiers']:
                        prop = m.Property.objects.get(display_id=json_qualifier['property'])
                        json_qsnak = json_qualifier['snak']
                        json_snaktype = json_qsnak['type']
                        qsnak = m.PropertySnak(property=prop)
                        if json_snaktype == 'Item' and json_qsnak['value']['item']['tokenId'] in unknown_entities:
                            qsnak.type = m.PropertySnak.Type.SOME_VALUE
                        else:
                            qsnak.type = m.PropertySnak.Type.VALUE
                            qsnak.value = json_to_python(json_snaktype, json_qsnak['value'])
                        qsnak.save()
                        qualifier = m.Qualifier(statement=statement, snak=qsnak)
                        qualifier.save()


                    for json_record in snak['referenceRecords']:
                        record = m.ReferenceRecord(statement=statement)
                        record.save()

                        for json_reference in json_record:
                            prop = m.Property.objects.get(display_id=json_reference['property'])
                            json_rsnak = json_reference['snak']
                            json_snaktype = json_rsnak['type']
                            rsnak = m.PropertySnak(property=prop)
                            if json_snaktype == 'Item' and json_value['value']['item']['tokenId'] in unknown_entities:
                                rsnak.type = m.PropertySnak.Type.SOME_VALUE
                            else:
                                rsnak.type = m.PropertySnak.Type.VALUE
                                rsnak.value = json_to_python(json_snaktype, json_rsnak['value'])
                            rsnak.save()
                            reference = m.ReferenceSnak(reference=record, snak=rsnak)
                            reference.save()

        return JsonResponse({'message': "ok"})
