from django.test import TestCase

import wikibase.models as m


def check_has_described_entity_fields(test_case, entity) -> None:
    test_case.assertIsInstance(entity.labels, m.MultilingualTextValue)
    test_case.assertEqual(0, entity.labels.monolingualtextvalue_set.count())
    test_case.assertIsInstance(entity.descriptions, m.MultilingualTextValue)
    test_case.assertEqual(0, entity.descriptions.monolingualtextvalue_set.count())
    test_case.assertIsInstance(entity.aliases, m.MultilingualMultiTextValue)
    test_case.assertEqual(0, entity.aliases.monolingualmultitextvalue_set.count())


class DescribedEntityTestCase(TestCase):
    def test_creation(self):
        de = m.DescribedEntity.objects.create()
        self.assertIsInstance(de, m.DescribedEntity)
        check_has_described_entity_fields(self, de)


class ItemTestCase(TestCase):
    def test_creation(self):
        item = m.Item.objects.create()
        self.assertIsInstance(item, m.Item)
        check_has_described_entity_fields(self, item)
        self.assertEqual(11, item.id) # 7 datatypes + 3 multi*textvalue = 10; so new item is 11
        self.assertEqual(1, item.display_id)

    def test_second_display_id(self):
        item1 = m.Item.objects.create()
        item2 = m.Item.objects.create()
        self.assertEqual(1, item1.display_id)
        self.assertEqual(2, item2.display_id)

    def test_second_display_id_after_new_property(self):
        item1 = m.Item.objects.create()
        prop = m.Property.objects.create(data_type=m.Datatype.objects.get(class_name='Item'))
        item2 = m.Item.objects.create()
        self.assertEqual(1, item1.display_id)
        self.assertEqual(1, prop.display_id)
        self.assertEqual(2, item2.display_id)

class PropertyTestCase(TestCase):
    def setUp(self):
        self.data_type = m.Datatype.objects.get(class_name='Item')

    def test_creation(self):
        prop = m.Property.objects.create(data_type=self.data_type)
        self.assertIsInstance(prop, m.Property)
        check_has_described_entity_fields(self, prop)
        self.assertEqual(11, prop.id) # 7 datatypes + 3 multi*textvalue = 10; so new property is 11
        self.assertEqual(1, prop.display_id)

    def test_second_display_id(self):
        prop1 = m.Property.objects.create(data_type=self.data_type)
        prop2 = m.Property.objects.create(data_type=self.data_type)
        self.assertEqual(1, prop1.display_id)
        self.assertEqual(2, prop2.display_id)

    def test_second_display_id_after_new_item(self):
        prop1 = m.Property.objects.create(data_type=self.data_type)
        item = m.Item.objects.create()
        prop2 = m.Property.objects.create(data_type=self.data_type)
        self.assertEqual(1, prop1.display_id)
        self.assertEqual(1, item.display_id)
        self.assertEqual(2, prop2.display_id)


class DataTypeTestCase(TestCase):
    def test_datatype_matches_class(self):
        self.assertEqual(m.Datatype.objects.get(class_name='Item').type, m.Item)
        self.assertEqual(m.Datatype.objects.get(class_name='Property').type, m.Property)
        self.assertEqual(m.Datatype.objects.get(class_name='StringValue').type, m.StringValue)
        self.assertEqual(m.Datatype.objects.get(class_name='QuantityValue').type, m.QuantityValue)
        self.assertEqual(m.Datatype.objects.get(class_name='TimeValue').type, m.TimeValue)
        self.assertEqual(m.Datatype.objects.get(class_name='GlobeCoordinatesValue').type, m.GlobeCoordinatesValue)
        self.assertEqual(m.Datatype.objects.get(class_name='MonolingualTextValue').type, m.MonolingualTextValue)
