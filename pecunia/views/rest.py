from rest_framework import viewsets, permissions
from rest_framework.response import Response

from pecunia.models import Item, Property, Statement
from pecunia.serializers import ItemSerializer, PropertySerializer, StatementSerializer


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

    def list(self, request, *args, **kwargs):
        """
        Transforme la liste en dict avec clé Q<display_id>.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Transformer la liste en dict préfixé
        prefixed_data = {item['id'] : item for item in data}

        return Response(prefixed_data)


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

    def list(self, request, *args, **kwargs):
        """
        Transforme la liste en dict avec clé Q<display_id>.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Transformer la liste en dict préfixé
        prefixed_data = {item['id'] : item for item in data}

        return Response(prefixed_data)


class StatementViewSet(viewsets.ModelViewSet):
    queryset = Statement.objects.all()
    serializer_class = StatementSerializer
    permission_classes = [permissions.IsAuthenticated]
