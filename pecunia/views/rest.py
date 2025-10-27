from rest_framework import viewsets, permissions

from pecunia.models import Item, Property
from pecunia.serializers import ItemSerializer, PropertySerializer


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().order_by('display_id')
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'display_id'

    def get_queryset(self):
        qs = super().get_queryset()

        query_params = self.request.query_params
        if 'label_like' in query_params:
            qs = qs.filter(labels__text__contains=query_params.get('label_like'))
        return qs


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all().order_by('display_id')
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'display_id'

    def get_queryset(self):
        qs = super().get_queryset()

        query_params = self.request.query_params
        if 'label_like' in query_params:
            qs = qs.filter(labels__text__contains=query_params.get('label_like'))
        return qs
