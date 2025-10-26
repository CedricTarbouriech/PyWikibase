from rest_framework import viewsets, permissions

from pecunia.models import Item, Property
from pecunia.serializers import ItemSerializer, PropertySerializer, LabelSerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().order_by('display_id')
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'display_id'

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by('display_id')
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
