import json

from django.test import Client
from django.test import TestCase

import wikibase.models as m


class CreateEntityTestCase(TestCase):

    def test_create_property(self):
        data_type = m.Datatype.objects.get(class_name='Item')
        prop = m.Property(data_type=data_type)
        prop.save()
        self.assertIsInstance(prop, m.Property)
        self.assertEqual(prop.data_type, data_type)


class ApiTestCase(TestCase):
    def test_api_items(self):
        c = Client()
        self.assertEqual(json.loads(c.get("/api/items/").content), [])
        m.Item.objects.create()
        self.assertEqual(json.loads(c.get("/api/items/").content),
                         [
                             {'display_id': 1,
                              'labels': {},
                              'descriptions': {},
                              'aliases': {},
                              'claims': {}
                              }
                         ]
                         )
