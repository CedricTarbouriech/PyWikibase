import random as rd

from django.core.exceptions import ValidationError
from django.test import TestCase

import pecunia.models as m


class CreateEntityTestCase(TestCase):
    def test_create_item(self):
        item = m.Item()
        item.save()
        self.assertIsInstance(item, m.Item)


class ReadItemTestCase(TestCase):
    def test_get_item_list(self):
        self.assertEqual(m.Item.objects.count(), 0)
        item1 = m.Item.objects.create()
        self.assertEqual(m.Item.objects.count(), 1)
        self.assertEqual(set(m.Item.objects.all()), {item1})
        item2 = m.Item.objects.create()
        self.assertEqual(m.Item.objects.count(), 2)
        self.assertEqual(set(m.Item.objects.all()), {item1, item2})

    def test_get_items_by_condition(self):
        self.fail("not yet implemented")

    def test_get_item_by_display_id(self):
        items = [m.Item.objects.create() for _ in range(10)]
        item = rd.choice(items)
        self.assertEqual(m.Item.objects.get(display_id=item.display_id), item)

    def test_get_item_with_unknown_display_id(self):
        # noinspection PyTypeChecker
        with self.assertRaises(m.Item.DoesNotExist):
            m.Item.objects.get(display_id=999)


class EditItemTestCase(TestCase):
    def test_add_property_wrong_datatype(self):
        string_dt = m.Datatype.objects.create(class_name='StringValue')
        i1 = m.Item.objects.create()
        i2 = m.Item.objects.create()
        p = m.Property(data_type=string_dt)
        p.save()
        with self.assertRaises(AssertionError):
            i1.add_value(p, i2)


class AddPropertyToItemTestCase(TestCase):
    def setUp(self):
        item_dt = m.Datatype.objects.get(class_name='Item')
        self.i1 = m.Item.objects.create()
        self.i2 = m.Item.objects.create()
        self.p = m.Property(data_type=item_dt)
        self.p.save()

    def test_add_property(self):
        statement = self.i1.add_value(self.p, self.i2)
        self.assertEqual(statement.subject, self.i1)
        self.assertIsInstance(statement.mainsnak, m.PropertySnak)
        self.assertEqual(statement.mainsnak.property, self.p)
        self.assertEqual(statement.mainsnak.value, self.i2)

    def test_default_rank_is_0(self):
        statement = self.i1.add_value(self.p, self.i2)
        self.assertEqual(statement.rank, 0)

    def test_set_rank_to_0(self):
        statement = self.i1.add_value(self.p, self.i2, rank=0)
        self.assertEqual(statement.rank, 0)

    def test_set_rank_to_minus_1(self):
        statement = self.i1.add_value(self.p, self.i2, rank=-1)
        self.assertEqual(statement.rank, -1)

    def test_set_rank_to_1(self):
        statement = self.i1.add_value(self.p, self.i2, rank=1)
        self.assertEqual(statement.rank, 1)

    def test_set_rank_to_incorrect_value(self):
        with self.assertRaises(ValidationError):
            self.i1.add_value(self.p, self.i2, rank=2)
        with self.assertRaises(ValidationError):
            self.i1.add_value(self.p, self.i2, rank=-2)

    # self.assertEqual(len(statement.references), 0) TODO Check that there are no references
