import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView

import pecunia.models as m
from pecunia.forms import DocumentMetadataForm, DocumentTextForm
from pecunia.models import Document, PropertyMapping, ItemMapping
from .api import json_to_python
from .wikibase import InstanceDashboardView


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
            document.set_label(form.cleaned_data['title_language'], form.cleaned_data['title'])
            title = m.MonolingualTextValue(language=form.cleaned_data['title_language'],
                                           text=form.cleaned_data['title'])
            title.save()
            document.set_title(title)
            document.save()
            self.kwargs['display_id'] = document.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('document_display', kwargs=self.kwargs)


class DocumentUpdateText(LoginRequiredMixin, FormView):
    template_name = 'pecunia/document_annotator.html'
    form_class = DocumentTextForm

    def form_valid(self, form):
        display_id = self.kwargs['display_id']
        document = Document.get_by_id(display_id)
        document.add_or_set_value(PropertyMapping.get('language'), m.ItemMapping.get(form.cleaned_data['language']))
        document.add_or_set_value(PropertyMapping.get('text'),
                                  m.StringValue.objects.create(value=form.cleaned_data['text']))
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
            print(document.get_value(PropertyMapping.get('language')))
            kwargs["initial"] = {
                'text': document.get_value(PropertyMapping.get('text')),
                'language': ItemMapping.get_key(document.get_value(PropertyMapping.get('language')))
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
        with transaction.atomic():
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
            new_items = {}
            for new_item in reconciliations['newItems']:
                items[new_item['tokenId']] = m.Item.objects.create()
                new_items[new_item['tokenId']] = items[new_item['tokenId']].display_id

            for linked_items in reconciliations['linkedItems']:
                items[linked_items['token']['tokenId']] = m.Item.objects.get(display_id=linked_items['qid'])

            schemata = data['schemas']
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
                        print(f"snak {snak}")
                        json_snaktype = snak['mainSnak']['type']

                        mainsnak = m.PropertySnak(property=prop)
                        if snak['mainSnak']['snakType'] == 'somevalue':
                            mainsnak.type = m.PropertySnak.Type.SOME_VALUE
                        elif snak['mainSnak']['snakType'] == 'novalue':
                            mainsnak.type = m.PropertySnak.Type.NO_VALUE
                        else:
                            mainsnak.type = m.PropertySnak.Type.VALUE
                            if json_snaktype == 'Item':
                                mainsnak.value = items[snak['mainSnak']['value']['item']['tokenId']]
                            else:
                                mainsnak.value = json_to_python(json_snaktype, snak['mainSnak']['value'])
                            print(json_snaktype, snak['mainSnak']['value'], mainsnak.value)
                        mainsnak.save()
                        statement = m.Statement(subject=item, mainsnak=mainsnak, rank=0)
                        statement.save()

                        for json_qualifier in snak['qualifiers']:
                            qual_prop = m.Property.objects.get(display_id=json_qualifier['property'])
                            json_qsnak = json_qualifier['snak']
                            json_snaktype = json_qsnak['type']
                            qsnak = m.PropertySnak(property=qual_prop)
                            if json_qsnak['snakType'] == 'somevalue':
                                qsnak.type = m.PropertySnak.Type.SOME_VALUE
                            elif json_qsnak['snakType'] == 'novalue':
                                qsnak.type = m.PropertySnak.Type.NO_VALUE
                            else:
                                qsnak.type = m.PropertySnak.Type.VALUE
                                if json_snaktype == 'Item':
                                    qsnak.value = items[json_qsnak['value']['item']['tokenId']]
                                else:
                                    qsnak.value = json_to_python(json_snaktype, json_qsnak['value'])
                            qsnak.save()
                            qualifier = m.Qualifier(statement=statement, snak=qsnak)
                            qualifier.save()

                        for json_record in snak['referenceRecords']:
                            record = m.ReferenceRecord(statement=statement)
                            record.save()

                            for json_reference in json_record:
                                ref_prop = m.Property.objects.get(display_id=json_reference['property'])
                                json_rsnak = json_reference['snak']
                                json_snaktype = json_rsnak['type']
                                rsnak = m.PropertySnak(property=ref_prop)
                                print(json_reference)
                                if json_rsnak['snakType'] == 'somevalue':
                                    rsnak.type = m.PropertySnak.Type.SOME_VALUE
                                elif json_rsnak['snakType'] == 'novalue':
                                    rsnak.type = m.PropertySnak.Type.NO_VALUE
                                else:
                                    rsnak.type = m.PropertySnak.Type.VALUE
                                    if json_snaktype == 'Item':
                                        rsnak.value = items[json_rsnak['value']['item']['tokenId']]
                                    else:
                                        rsnak.value = json_to_python(json_snaktype, json_rsnak['value'])
                                rsnak.save()
                                reference = m.ReferenceSnak(reference=record, snak=rsnak)
                                reference.save()

        return JsonResponse({'message': "ok", 'newItems': new_items})
