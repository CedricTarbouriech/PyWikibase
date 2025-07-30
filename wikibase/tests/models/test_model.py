from django.test import TestCase

import wikibase.models as m


def check_has_described_entity_fields(test_case, entity) -> None:
    test_case.assertEqual(0, entity.labels.count())
    test_case.assertEqual(0, entity.descriptions.count())
    test_case.assertEqual(0, entity.aliases.count())


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
        self.assertEqual(9, item.id)  # 8 datatypes ; so new item is 9
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
        print(m.Value.objects.all())
        self.assertEqual(9, prop.id)  # 8 datatypes ; so new item is 9
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


class DeleteTestCase(TestCase):
    def test_delete_snak(self):
        self.assertEqual(m.QuantityValue.objects.count(), 0)
        self.assertEqual(m.PropertySnak.objects.count(), 0)
        p = m.Property.objects.create(data_type=m.Datatype.objects.get(class_name='QuantityValue'))
        v = m.QuantityValue.objects.create(number=7)
        sn = m.PropertySnak.objects.create(property=p, type=0, value=v)
        self.assertEqual(m.QuantityValue.objects.count(), 1)
        self.assertEqual(m.PropertySnak.objects.count(), 1)
        self.assertEqual(m.QuantityValue.objects.all()[0], v)
        self.assertEqual(m.PropertySnak.objects.all()[0], sn)

        sn.delete()

        self.assertEqual(m.PropertySnak.objects.count(), 0)
        self.assertEqual(m.QuantityValue.objects.count(), 0)

    def test_delete_statement(self):
        self.assertEqual(m.QuantityValue.objects.count(), 0)
        self.assertEqual(m.PropertySnak.objects.count(), 0)
        self.assertEqual(m.Statement.objects.count(), 0)
        i = m.Item.objects.create()
        p = m.Property.objects.create(data_type=m.Datatype.objects.get(class_name='QuantityValue'))
        v = m.QuantityValue.objects.create(number=7)
        sn = m.PropertySnak.objects.create(property=p, type=0, value=v)
        st = m.Statement.objects.create(subject=i, mainsnak=sn, rank=0)
        self.assertEqual(m.QuantityValue.objects.count(), 1)
        self.assertEqual(m.PropertySnak.objects.count(), 1)
        self.assertEqual(m.Statement.objects.count(), 1)
        self.assertEqual(m.QuantityValue.objects.all()[0], v)
        self.assertEqual(m.PropertySnak.objects.all()[0], sn)
        self.assertEqual(m.Statement.objects.all()[0], st)

        st.delete()

        self.assertEqual(m.Statement.objects.count(), 0)
        self.assertEqual(m.PropertySnak.objects.count(), 0)
        self.assertEqual(m.QuantityValue.objects.count(), 0)
