from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from pecunia.models import Item, Property, PropertyMapping, ItemMapping, Datatype, Document


class TestDocumentMetadataForm(TestCase):
    def setUp(self):
        self.document_type = Item.objects.create()
        ItemMapping.objects.create(key='document', item=self.document_type)
        self.is_a_property = Property.objects.create(data_type=Datatype.objects.get(class_name='Item'))
        PropertyMapping.objects.create(key='is_a', property=self.is_a_property)

    def test1(self):
        form_data = {
            'title': 'euieiu',
            'title_language': 'en',
            'source_type': '1',
            'author': '11',
            'author_function': '1',
            'place': '10'
        }

        self.assertEqual(Document.objects.count(), 0)
        response = self.client.post(reverse('document_create'), data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Document.objects.count(), 1)
        print(response, response.status_code)
        print()
