import random as rd

from django.core.exceptions import ValidationError
from django.test import TestCase

import wikibase.api as api
import wikibase.models as m


class CreateEntityTestCase(TestCase):
    def test_create_item(self):
        item = api.create_item()
        self.assertIsInstance(item, m.Item)


class ReadItemTestCase(TestCase):
    def test_get_item_list(self):
        self.assertEqual(len(api.get_items()), 0)
        item1 = api.create_item()
        self.assertEqual(len(api.get_items()), 1)
        self.assertEqual(set(api.get_items()), {item1})
        item2 = api.create_item()
        self.assertEqual(len(api.get_items()), 2)
        self.assertEqual(set(api.get_items()), {item1, item2})

    def test_get_items_by_condition(self):
        self.fail("not yet implemented")

    def test_get_item_by_display_id(self):
        items = [api.create_item() for _ in range(10)]
        item = rd.choice(items)
        self.assertEqual(api.get_item(display_id=item.display_id), item)

    def test_get_item_with_unknown_display_id(self):
        # noinspection PyTypeChecker
        with self.assertRaises(m.Item.DoesNotExist):
            api.get_item(display_id=999)


class EditItemTestCase(TestCase):
    def test_add_property_wrong_datatype(self):
        string_dt = m.Datatype.objects.create(class_name='StringValue')
        i1 = api.create_item()
        i2 = api.create_item()
        p = api.create_property(string_dt)
        with self.assertRaises(AssertionError):
            api.add_value_property(i1, p, i2)


class AddPropertyToItemTestCase(TestCase):
    def setUp(self):
        item_dt = m.Datatype.objects.get(class_name='Item')
        self.i1 = api.create_item()
        self.i2 = api.create_item()
        self.p = api.create_property(item_dt)

    def test_add_property(self):
        statement = api.add_value_property(self.i1, self.p, self.i2)
        self.assertEqual(statement.subject, self.i1)
        self.assertIsInstance(statement.mainSnak, m.PropertyValueSnak)
        self.assertEqual(statement.mainSnak.property, self.p)
        self.assertEqual(statement.mainSnak.value, self.i2)

    def test_default_rank_is_0(self):
        statement = api.add_value_property(self.i1, self.p, self.i2)
        self.assertEqual(statement.rank, 0)

    def test_set_rank_to_0(self):
        statement = api.add_value_property(self.i1, self.p, self.i2, rank=0)
        self.assertEqual(statement.rank, 0)

    def test_set_rank_to_minus_1(self):
        statement = api.add_value_property(self.i1, self.p, self.i2, rank=-1)
        self.assertEqual(statement.rank, -1)

    def test_set_rank_to_1(self):
        statement = api.add_value_property(self.i1, self.p, self.i2, rank=1)
        self.assertEqual(statement.rank, 1)

    def test_set_rank_to_incorrect_value(self):
        with self.assertRaises(ValidationError):
            api.add_value_property(self.i1, self.p, self.i2, rank=2)
        with self.assertRaises(ValidationError):
            api.add_value_property(self.i1, self.p, self.i2, rank=-2)

    # self.assertEqual(len(statement.references), 0) TODO Check that there are no references
