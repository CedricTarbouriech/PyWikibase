import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import View

from wikibase import models as m


class PropertyApiView(View):
    def get(self, request, prop_id=None):
        if prop_id:
            prop = m.Property.objects.get(display_id=prop_id)
            return JsonResponse({'type': prop.data_type.class_name,
                                 'labels': {mlt.lang_code: mlt.value for mlt in
                                            prop.labels.monolingualtextvalue_set.all()}})
        else:
            properties = {}
            for prop in m.Property.objects.all():
                properties[prop.display_id] = {'type': prop.data_type.class_name,
                                               'labels': {mlt.lang_code: mlt.value for mlt in
                                                          prop.labels.monolingualtextvalue_set.all()}}
            return JsonResponse(properties)


class ItemApiView(View):
    def get(self, request):
        items = {}
        for item in m.Item.objects.all():
            items[item.display_id] = {
                'labels': {mlt.lang_code: mlt.value for mlt in item.labels.monolingualtextvalue_set.all()}}
        return JsonResponse(items)


class StatementAddApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode('utf-8'))
        type_field_value = post_data.get('snak_type')
        prop = m.Property.objects.get(display_id=post_data.get('prop_id'))
        # FIXME: Not compatible if we want to add statements to properties
        subject = m.Item.objects.get(display_id=post_data.get('entity_id'))

        snak = None
        if type_field_value == "0":
            value = None
            type_name = prop.data_type.class_name
            if type_name == 'Item':
                value = m.Item.objects.get(display_id=post_data['value']['item'])
            elif type_name == 'MonolingualTextValue':
                value = m.MonolingualTextValue(lang_code=post_data['value']['language'],
                                               value=post_data['value']['value'])
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
            else:
                raise Exception(f"Unknown datatype: {type_name}")
            snak = m.PropertyValueSnak(property=prop, value=value)
        elif type_field_value == "1":
            snak = m.PropertySomeValueSnak(property=prop)
        elif type_field_value == "2":
            snak = m.PropertyNoValueSnak(property=prop)
        else:
            raise Exception(f"Unknown snak type: {type_field_value}")

        snak.save()
        statement = m.Statement(subject=subject, mainSnak=snak, rank=0)
        statement.save()

        data = {
            'statement': [statement],
            'prop': prop,
            'item': subject
        }
        updated_html = render_to_string('widgets/property_table.html', data)
        return JsonResponse({'updatedHtml': updated_html})


class StatementApiView(View):
    def get(self, request, statement_id):
        statement = m.Statement.objects.get(id=statement_id)
        snak = statement.mainSnak
        value_presence_type = None
        value = None
        if type(snak) == m.PropertyValueSnak:
            value_presence_type = "0"
            property_type = snak.property.data_type.class_name
            if property_type == 'MonolingualTextValue':
                value = {
                    'lang': snak.value.lang_code,
                    'value': snak.value.value
                }
            elif property_type == 'StringValue':
                value = {'value': snak.value.value}
            elif property_type == 'Item':
                value = {'id': snak.value.display_id}
            elif property_type == 'QuantityValue':
                value = {'number': snak.value.number}
        elif type(snak) == m.PropertySomeValueSnak:
            value_presence_type = "1"
        elif type(snak) == m.PropertyNoValueSnak:
            value_presence_type = "2"
        snak_data = {
            'id': snak.id,
            'propertyId': snak.property.display_id,
            'propertyType': snak.property.data_type.class_name,
            'snak_type': value_presence_type,
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
        value = m.MonolingualTextValue(lang_code=value['language'], value=value['value'])
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


class StatementUpdateApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode('utf-8'))
        statement_id = post_data.get('statement_id')
        statement = m.Statement.objects.get(id=statement_id)

        main_snak = statement.mainSnak
        prop = main_snak.property
        prop_type = prop.property.data_type.class_name

        next_snak_type = int(post_data.get('snak_type'))
        new_snak = None

        if next_snak_type == 0:
            new_snak = m.PropertyValueSnak(property=prop, value=json_to_python(prop_type, post_data['value']))
        elif next_snak_type == 1:
            new_snak = m.PropertySomeValueSnak(property=prop)
        elif next_snak_type == 2:
            new_snak = m.PropertyNoValueSnak(property=prop)

        new_snak.save()

        statement.mainSnak = new_snak
        statement.rank = post_data.get('rank')
        statement.save()

        data = {
            'statement': [statement],
            'prop': prop,
            'item': statement.subject
        }
        updated_html = render_to_string('widgets/property_table.html', data, request)
        return JsonResponse({'updatedHtml': updated_html})


class StatementDeleteApiView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        post_data = json.loads(request.body.decode('utf-8'))
        statement_id = post_data.get('statement_id')
        statement = m.Statement.objects.get(id=statement_id)
        subject = statement.subject
        prop = statement.mainSnak.property
        main_snak = statement.mainSnak

        if main_snak == m.PropertyValueSnak and main_snak.property.data_type.class_name != "Item":
            main_snak.value.delete()
        statement.mainSnak.delete()
        statement.delete()

        return JsonResponse({'number': subject.statement_set.filter(mainSnak__propertysnak__property=prop).count()})
