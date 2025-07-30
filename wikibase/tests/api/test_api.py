import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

import wikibase.models as m


class CreateEntityTestCase(TestCase):

    def test_create_property(self):
        data_type = m.Datatype.objects.get(class_name='Item')
        prop = m.Property(data_type=data_type)
        prop.save()
        self.assertIsInstance(prop, m.Property)
        self.assertEqual(prop.data_type, data_type)


class ApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=User.objects.create_superuser('testuser'))

    def test_api_get_items(self):
        self.assertEqual(json.loads(self.client.get("/api/items/").content), [])
        m.Item.objects.create()
        self.assertEqual(json.loads(self.client.get("/api/items/").content),
                         [{
                             'display_id': 1,
                             'labels': {},
                             'descriptions': {},
                             'aliases': {},
                             'claims': {}
                         }])

    def test_api_create_item(self):
        response = self.client.post("/api/items/", {
            "labels": [{"language": "fr", "text": "test"}],
            'descriptions': [],
            'aliases': [],
            'claims': [{'mainsnak': {}, 'qualifiers': [{'snak': {}}], 'references': [{"snaks": [{'snak': {}}]}]}]
        }, content_type="application/json")
        print(response.status_code, response.content.decode())
        print(m.Item.objects.all())
        self.fail("eiei")

    def test_api_update_item(self):
        m.Item.objects.create()
        response = self.client.put("/api/items/1/", {
            'labels': [],
            'descriptions': [],
            'aliases': [],
            'claims': []
        }, content_type="application/json")
        print(response.status_code, response.content.decode())
        print(m.Item.objects.all())
        self.fail("eiei")
