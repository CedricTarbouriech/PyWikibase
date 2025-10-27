from collections import defaultdict

from rest_framework import serializers

from .models import Item, Property, Label, Description


class PrefixedByLanguageField(serializers.ListSerializer):
    def to_representation(self, data):
        grouped = defaultdict(list)
        for item in super().to_representation(data):
            grouped[item['language']] = item['text']
        return grouped


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['language', 'text']
        list_serializer_class = PrefixedByLanguageField


class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = ['language', 'text']
        list_serializer_class = PrefixedByLanguageField

class ItemSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, required=False, default=list(), read_only=True)
    descriptions = DescriptionSerializer(many=True, required=False, default=list(), read_only=True)

    class Meta:
        model = Item
        fields = ['display_id', 'labels', 'descriptions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if not request or self.context.get('view').action == 'retrieve':
            return

        fields_param = request.query_params.get('fields', '')
        fields = fields_param.split(',') if fields_param else []

        if 'labels' not in fields:
            self.fields.pop('labels', None)

        if 'descriptions' not in fields:
            self.fields.pop('descriptions', None)


class PropertySerializer(serializers.ModelSerializer):
    type = serializers.SlugRelatedField(
        read_only=True,
        slug_field='class_name',
        source='data_type'
    )
    labels = LabelSerializer(many=True, required=False, default=list(), read_only=True)
    descriptions = DescriptionSerializer(many=True, required=False, default=list(), read_only=True)

    class Meta:
        model = Property
        fields = ['display_id', 'type', 'labels', 'descriptions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if not request or self.context.get('view').action == 'retrieve':
            return

        fields_param = request.query_params.get('fields', '')
        fields = fields_param.split(',') if fields_param else []

        if 'labels' not in fields:
            self.fields.pop('labels', None)

        if 'descriptions' not in fields:
            self.fields.pop('descriptions', None)
