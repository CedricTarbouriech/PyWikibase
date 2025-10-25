from django.test import TestCase

from pecunia.models import Datatype, Item, Property, StringValue, UrlValue, QuantityValue, TimeValue, \
    GlobeCoordinatesValue, MonolingualTextValue, UnknownDatatypeException, DataValue


class DataTypeTestCase(TestCase):
    def test_datatype_matches_class(self):
        self.assertEqual(Datatype.objects.get(class_name='Item').type, Item)
        self.assertEqual(Datatype.objects.get(class_name='Property').type, Property)
        self.assertEqual(Datatype.objects.get(class_name='StringValue').type, StringValue)
        self.assertEqual(Datatype.objects.get(class_name='UrlValue').type, UrlValue)
        self.assertEqual(Datatype.objects.get(class_name='QuantityValue').type, QuantityValue)
        self.assertEqual(Datatype.objects.get(class_name='TimeValue').type, TimeValue)
        self.assertEqual(Datatype.objects.get(class_name='GlobeCoordinatesValue').type, GlobeCoordinatesValue)
        self.assertEqual(Datatype.objects.get(class_name='MonolingualTextValue').type, MonolingualTextValue)
        with self.assertRaises(UnknownDatatypeException):
            dt = Datatype.objects.create(class_name='TestValue')
            # This last line is just here to raise the exception
            self.assertIsInstance(DataValue, dt.type)

