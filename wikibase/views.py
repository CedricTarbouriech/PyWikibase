import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, TemplateView, View

from wikibase import models as m
from wikibase.forms import ItemLabelDescriptionForm, PropertyLabelDescriptionForm
from wikibase.models import ItemMapping, PropertyMapping, PropertyType


class PropertyApiView(View):
    def get(self, request, prop_id=None):
        if prop_id:
            prop = m.Property.objects.get(display_id=prop_id)
            return JsonResponse({
                'type': prop.data_type.class_name,
                'labels': {mlt.language: mlt.text for mlt in prop.labels.all()}
            })
        else:
            properties = {}
            for prop in m.Property.objects.all():
                properties[prop.display_id] = {
                    'type': prop.data_type.class_name,
                    'labels': {mlt.language: mlt.text for mlt in prop.labels.all()}
                }
            return JsonResponse(properties)


class ItemApiView(View):
    def get(self, request):
        items = {}
        for item in m.Item.objects.all():
            items[item.display_id] = {'labels': {mlt.language: mlt.text for mlt in item.labels.all()}}
        return JsonResponse(items)


class SearchItemApiView(View):
    def get(self, request, search):
        items = {}
        for item in m.Item.objects.filter(labels__text__contains=search).distinct():
            items[item.display_id] = {
                'labels': {mlt.language: mlt.text for mlt in item.labels.all()},
                'descriptions': {mlt.language: mlt.text for mlt in item.descriptions.all()}
            }
        return JsonResponse(items)


class NewItemApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            item = m.Item.objects.create()
            post_data = json.loads(request.body.decode('utf-8'))
            if post_data:
                for statement in post_data['statements']:
                    prop = None
                    value = None
                    if isinstance(statement['property'], str):
                        prop = PropertyMapping.get(statement['property'])
                    elif isinstance(statement['property'], int):
                        prop = m.Property.objects.get(display_id=statement['property'])
                    if isinstance(statement['value'], str):
                        value = ItemMapping.get(statement['value'])
                    elif isinstance(statement['value'], int):
                        value = m.Item.objects.get(display_id=statement['value'])

                    snak = m.PropertySnak(property=prop, value=value, type=0)
                    snak.save()
                    statement = m.Statement(subject=item, mainsnak=snak, rank=0)
                    statement.save()
        return JsonResponse({'display_id': item.display_id})


class StatementAddApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        with transaction.atomic():
            post_data = json.loads(request.body.decode('utf-8'))
            type_field_value = int(post_data.get('snak_type'))
            prop = m.Property.objects.get(display_id=post_data.get('prop_id'))
            # FIXME: Not compatible if we want to add statements to properties
            subject = m.Item.objects.get(display_id=post_data.get('entity_id'))

            value = None
            if type_field_value == PropertyType.VALUE:
                type_name = prop.data_type.class_name
                if type_name == 'Item':
                    value = m.Item.objects.get(display_id=post_data['value']['item'])
                elif type_name == 'MonolingualTextValue':
                    value = m.MonolingualTextValue(language=post_data['value']['language'],
                                                   text=post_data['value']['value'])
                    value.save()
                elif type_name == 'StringValue':
                    value = m.StringValue(value=post_data['value']['value'])
                    value.save()
                elif type_name == 'UrlValue':
                    value = m.UrlValue(value=post_data['value']['value'])
                    value.save()
                elif type_name == 'QuantityValue':
                    value = m.QuantityValue(number=post_data['value']['number'])
                    value.save()
                elif type_name == 'GlobeCoordinatesValue':
                    data = post_data['value']
                    value = m.GlobeCoordinatesValue(latitude=data['latitude'], longitude=data['longitude'],
                                                    precision='0.0000001', globe=ItemMapping.get('earth'))
                    value.save()
                else:
                    raise Exception(f"Unknown datatype: {type_name}")
            snak = m.PropertySnak(property=prop, value=value, type=type_field_value)
            snak.save()
            statement = m.Statement(subject=subject, mainsnak=snak, rank=post_data.get('rank'))
            statement.save()

            data = {
                'statement': [statement],
                'prop': prop,
                'item': subject
            }
            updated_html = render_to_string('wikibase/widgets/property_table.html', data, request=request)
        return JsonResponse({'updatedHtml': updated_html})


class StatementApiView(View):
    def get(self, request, statement_id):
        statement = m.Statement.objects.get(id=statement_id)
        snak = statement.mainsnak
        value_presence_type = None
        value = None
        value_presence_type = "0"
        property_type = snak.property.data_type.class_name
        if property_type == 'MonolingualTextValue':
            value = {
                'lang': snak.value.language,
                'value': snak.value.text
            }
        elif property_type == 'StringValue':
            value = {'value': snak.value.text}
        elif property_type == 'Item':
            value = {'id': snak.value.display_id}
        elif property_type == 'UrlValue':
            value = {'value': snak.value.value}
        elif property_type == 'QuantityValue':
            value = {'number': snak.value.number}
        elif property_type == 'GlobeCoordinatesValue':
            value = {'latitude': snak.value.latitude, 'longitude': snak.value.longitude}
        snak_data = {
            'id': snak.id,
            'propertyId': snak.property.display_id,
            'propertyType': snak.property.data_type.class_name,
            'snak_type': snak.type,
            'value': value
        }

        data = {
            'subject': statement.subject.display_id,
            'mainSnak': snak_data,
            'rank': statement.rank
        }
        return JsonResponse(data)


def json_to_python(type_name, value):
    if type_name == 'Item':
        return m.Item.objects.get(display_id=value['item'])
    elif type_name == 'MonolingualTextValue':
        value = m.MonolingualTextValue(language=value['language'], text=value['value'])
        value.save()
        return value
    elif type_name == 'StringValue':
        value = m.StringValue(value=value['value'])
        value.save()
        return value
    elif type_name == 'QuantityValue':
        value = m.QuantityValue(number=value['number'])
        value.save()
        return value
    elif type_name == 'GlobeCoordinatesValue':
        value = m.GlobeCoordinatesValue(latitude=value['latitude'],
                                        longitude=value['longitude'],
                                        precision='0.0000001',
                                        globe=ItemMapping.get('earth'))
        value.save()
        return value


class InstanceDashboardView(TemplateView):
    item_mapping_key = None

    def dispatch(self, request, *args, **kwargs):
        if not ItemMapping.has(self.item_mapping_key):
            raise Http404(f"Item mapping '{self.item_mapping_key}' does not exist.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        items = m.Item.objects.all()
        result = []
        is_a_prop = PropertyMapping.get('is_a')
        item_mapping = ItemMapping.get(self.item_mapping_key)
        for item in items:
            if not item.statements.exists():
                continue
            if item.statements.filter(mainsnak__property=is_a_prop,
                                      mainsnak__value=item_mapping).exists():
                result.append(item)

        context['items'] = result
        return context


class StatementUpdateApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode('utf-8'))
        statement_id = post_data.get('statement_id')
        statement = m.Statement.objects.get(id=statement_id)

        main_snak = statement.mainsnak
        prop = main_snak.property
        prop_type = prop.property.data_type.class_name

        next_snak_type = int(post_data.get('snak_type'))
        new_snak = m.PropertySnak(property=prop, value=json_to_python(prop_type, post_data['value']),
                                  type=next_snak_type)

        new_snak.save()

        statement.mainsnak = new_snak
        statement.rank = post_data.get('rank')
        statement.save()

        data = {
            'statement': [statement],
            'prop': prop,
            'item': statement.subject
        }
        updated_html = render_to_string('wikibase/widgets/property_table.html', data, request=request)
        return JsonResponse({'updatedHtml': updated_html})


class StatementDeleteApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode('utf-8'))
        statement_id = post_data.get('statement_id')
        statement = m.Statement.objects.get(id=statement_id)
        subject = statement.subject
        prop = statement.mainsnak.property

        statement.delete()

        return JsonResponse({'number': subject.statements.filter(mainsnak__property=prop).count()})


DEFAULT_PAGINATOR_LIMIT = 25


class ModelDashboardView(TemplateView):
    model = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.model.objects.all()
        paginator = Paginator(items, self.request.GET.get("limit") or DEFAULT_PAGINATOR_LIMIT)

        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context


class ItemDashboard(ModelDashboardView):
    template_name = 'wikibase/item_list.html'
    model = m.Item


class ItemDisplay(TemplateView):
    template_name = 'wikibase/item_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        item = m.Item.objects.get(display_id=self.kwargs['display_id'])
        context['item'] = item

        props = set()
        for statement_prop in item.statements.all():
            props.add(statement_prop.mainsnak.property)

        statements = []
        for prop in props:
            values = []
            for statement in item.statements.filter(mainsnak__property=prop):
                values.append(statement)
            statements.append((prop, values))
        context['statements'] = statements

        linked_items = []
        for stmt in m.Statement.objects.filter(mainsnak__value=item):
            linked_items.append(stmt.subject.display_id)
        context['linked_items'] = sorted(linked_items)
        return context


class ItemUpdateLabelDescription(LoginRequiredMixin, FormView):
    template_name = 'wikibase/item_update_labeldescription.html'
    form_class = ItemLabelDescriptionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        display_id = self.kwargs['display_id']
        lang = self.kwargs['lang']
        item = m.Item.objects.get(display_id=display_id)
        kwargs['display_id'] = display_id
        kwargs['initial']['language'] = lang
        try:
            label = item.labels.get(language=lang)
            kwargs['initial']['label'] = label.text
        except ObjectDoesNotExist:
            pass
        try:
            description = item.descriptions.get(language=lang)
            kwargs['initial']['description'] = description.text
        except ObjectDoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            item = m.Item.objects.get(display_id=self.kwargs['display_id'])
            language_code = self.kwargs['lang']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            if label:
                item.set_label(language_code, label)
            if description:
                item.add_description(language_code, description)
            self.kwargs['display_id'] = item.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('item_display', kwargs={'display_id': self.kwargs['display_id']})


class ItemCreation(LoginRequiredMixin, FormView):
    template_name = 'wikibase/item_creation.html'
    form_class = ItemLabelDescriptionForm

    def form_valid(self, form):
        if form.is_valid():
            # Creation of the property
            item = m.Item.objects.create()
            self.kwargs['display_id'] = item.display_id

            # Creation of the label and the description
            language_code = form.cleaned_data['language']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            if label:
                item.set_label(language_code, label)
            if description:
                item.add_description(language_code, description)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('item_display', kwargs=self.kwargs)


class ItemDelete(LoginRequiredMixin, TemplateView):
    template_name = 'wikibase/confirm_delete.html'
    success_url = reverse_lazy('item_list')

    def post(self, request, *args, **kwargs):
        if "confirm" in request.POST:
            m.Item.objects.get(display_id=self.kwargs['display_id']).delete()
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = f"Item Q{self.kwargs['display_id']}"
        return context


class PropertyDashboard(ModelDashboardView):
    template_name = 'wikibase/property_list.html'
    model = m.Property


class PropertyDisplay(DetailView):
    template_name = 'wikibase/property_detail.html'

    def get_object(self, queryset=None):
        return m.Property.objects.get(display_id=self.kwargs['display_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            prop = kwargs['object']
            stmts = m.Statement.objects.filter(mainsnak__property=prop)
            linked_items = []
            for stmt in stmts:
                linked_items.append(stmt.subject.display_id)
            context['linked_items'] = sorted(linked_items)
        except ObjectDoesNotExist as e:
            raise Http404 from e

        return context


class PropertyCreation(LoginRequiredMixin, FormView):
    template_name = 'wikibase/property_creation.html'
    form_class = PropertyLabelDescriptionForm

    def form_valid(self, form):
        if form.is_valid():
            # Creation of the property
            datatype = form.cleaned_data['type']
            prop = m.Property(data_type=m.Datatype.objects.get(class_name=datatype))
            prop.save()
            self.kwargs['display_id'] = prop.display_id

            # Creation of the label and the description
            language_code = form.cleaned_data['language']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            if label:
                prop.set_label(language_code, label)
            if description:
                prop.add_description(language_code, description)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('property_display', kwargs=self.kwargs)


class PropertyUpdateLabelDescription(LoginRequiredMixin, FormView):
    template_name = 'wikibase/property_update_labeldescription.html'
    form_class = PropertyLabelDescriptionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        display_id = self.kwargs['display_id']
        lang = self.kwargs['lang']
        prop = m.Property.objects.get(display_id=display_id)
        kwargs['display_id'] = display_id
        kwargs['initial']['language'] = lang
        kwargs['initial']['type'] = prop.data_type.class_name
        try:
            label = prop.labels.get(language=lang)
            kwargs['initial']['label'] = label.text
        except ObjectDoesNotExist:
            pass
        try:
            description = prop.descriptions.get(language=lang)
            kwargs['initial']['description'] = description.text
        except ObjectDoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            prop = m.Property.objects.get(display_id=self.kwargs['display_id'])
            language_code = self.kwargs['lang']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            if label:
                prop.set_label(language_code, label)
            if description:
                prop.add_description(language_code, description)
            self.kwargs['display_id'] = prop.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('property_display', kwargs={'display_id': self.kwargs['display_id']})


class PropertyDelete(LoginRequiredMixin, TemplateView):
    template_name = 'wikibase/confirm_delete.html'
    success_url = reverse_lazy('property_list')

    def post(self, request, *args, **kwargs):
        if "confirm" in request.POST:
            m.Property.objects.get(display_id=self.kwargs['display_id']).delete()
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = f"Property P{self.kwargs['display_id']}"
        return context
