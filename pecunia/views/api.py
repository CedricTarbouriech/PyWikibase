import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import View

import pecunia.models as m
from pecunia.models import ItemMapping, PropertyMapping, PropertySnak


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


class SearchApiView(View):
    result_class = None

    def get(self, request, search):
        results = {}
        for item in self.result_class.objects.filter(labels__text__contains=search).distinct():
            results[item.display_id] = {
                'labels': {mlt.language: mlt.text for mlt in item.labels.all()},
                'descriptions': {mlt.language: mlt.text for mlt in item.descriptions.all()}
            }
        return JsonResponse(results)


class SearchItemApiView(View):
    result_class = m.Item


class SearchPropertyApiView(View):
    result_class = m.Property


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


class QualifierAddApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode('utf-8'))
        statement = m.Statement.objects.get(id=(int(post_data['statement_id'])))
        prop = m.Property.objects.get(display_id=(int(post_data['prop_id'])))
        with transaction.atomic():
            value = None
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
            snak = m.PropertySnak(property=prop, value=value, type=m.PropertySnak.Type.VALUE)
            snak.save()
            statement.qualifiers.create(snak=snak)
            statement.save()

            data = {
                'stat': statement
            }
            updated_html = render_to_string('wikibase/widgets/qualifiers_table.html', data, request=request)
        return JsonResponse({'updatedHtml': updated_html})


class QualifierDeleteApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode('utf-8'))
        qualifier_id = post_data.get('qualifier_id')
        qualifier = m.Qualifier.objects.get(id=qualifier_id)
        statement = qualifier.statement
        qualifier.delete()

        return JsonResponse({'number': statement.qualifiers.count()})


class StatementAddApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode('utf-8'))
        type_field_value = int(post_data.get('snak_type'))
        prop = m.Property.objects.get(display_id=post_data.get('prop_id'))
        with transaction.atomic():
            # FIXME: Not compatible if we want to add statements to properties
            subject = m.Item.objects.get(display_id=post_data.get('entity_id'))

            snak = None
            if type_field_value == PropertySnak.Type.VALUE:
                value = None
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
            elif type_field_value == PropertySnak.Type.SOME_VALUE:
                snak = m.PropertySnak(property=prop, type=type_field_value)
            elif type_field_value == PropertySnak.Type.NO_VALUE:
                snak = m.PropertySnak(property=prop, type=type_field_value)
            else:
                print("error")  # FIXME

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
            value = {'value': snak.value.value}
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
    elif type_name == 'UrlValue':
        value = m.UrlValue(value=value['value'])
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
