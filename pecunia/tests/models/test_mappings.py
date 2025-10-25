from django.db.utils import IntegrityError
from django.test import TestCase

from pecunia.models import Property, Datatype, UnknownMappingException, PropertyMapping, ItemMapping, Item


class PropertyMappingTestCase(TestCase):
    def test_non_existing_mapping(self):
        self.assertFalse(PropertyMapping.has('test'))
        with self.assertRaises(UnknownMappingException):
            PropertyMapping.get('test')

    def test_existing_mapping(self):
        prop = Property.objects.create(data_type=Datatype.objects.get(class_name='StringValue'))
        PropertyMapping.objects.create(key='test', property=prop)
        self.assertTrue(PropertyMapping.has('test'))
        self.assertEqual(prop, PropertyMapping.get('test'))

    def test_same_key_used_twice(self):
        prop1 = Property.objects.create(data_type=Datatype.objects.get(class_name='StringValue'))
        prop2 = Property.objects.create(data_type=Datatype.objects.get(class_name='StringValue'))
        PropertyMapping.objects.create(key='test', property=prop1)
        with self.assertRaises(IntegrityError):
            PropertyMapping.objects.create(key='test', property=prop2)

    def test_same_property_used_twice(self):
        prop = Property.objects.create(data_type=Datatype.objects.get(class_name='StringValue'))
        PropertyMapping.objects.create(key='test1', property=prop)
        with self.assertRaises(IntegrityError):
            PropertyMapping.objects.create(key='test2', property=prop)


class ItemMappingTestCase(TestCase):
    def test_non_existing_mapping(self):
        self.assertFalse(ItemMapping.has('test'))
        with self.assertRaises(UnknownMappingException):
            ItemMapping.get('test')

    def test_existing_mapping(self):
        item = Item.objects.create()
        ItemMapping.objects.create(key='test', item=item)
        self.assertTrue(ItemMapping.has('test'))
        self.assertEqual(item, ItemMapping.get('test'))

    def test_same_key_used_twice(self):
        item1 = Item.objects.create()
        item2 = Item.objects.create()
        ItemMapping.objects.create(key='test', item=item1)
        with self.assertRaises(IntegrityError):
            ItemMapping.objects.create(key='test', item=item2)

    def test_same_property_used_twice(self):
        item = Item.objects.create()
        ItemMapping.objects.create(key='test1', item=item)
        with self.assertRaises(IntegrityError):
            ItemMapping.objects.create(key='test2', item=item)
