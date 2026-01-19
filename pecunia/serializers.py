from collections import defaultdict

from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField

from .models import Item, Property, Label, Description, Alias, Statement, PropertySnak, ReferenceRecord, Qualifier, \
    ReferenceSnak


class SingleValuePrefixedByLanguageField(serializers.ListSerializer):
    def to_representation(self, data):
        grouped = defaultdict(list)
        for item in super().to_representation(data):
            grouped[item['language']] = item['text']
        return grouped


def build_list_serializer(get_key, get_value=lambda item: item):
    class MultipleValuesPrefixedByPropertyField2(serializers.ListSerializer):
        def to_representation(self, data):
            grouped = defaultdict(list)
            for item in super().to_representation(data):
                if get_key(item) not in grouped:
                    grouped[get_key(item)] = []
                grouped[get_key(item)].append(get_value(item))
            return grouped

    return MultipleValuesPrefixedByPropertyField2


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['language', 'text']
        list_serializer_class = SingleValuePrefixedByLanguageField


class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = ['language', 'text']
        list_serializer_class = SingleValuePrefixedByLanguageField


class AliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alias
        fields = ['language', 'text']
        list_serializer_class = build_list_serializer(lambda item: item['language'], lambda item: item['text'])


class BaseSnakSerializer(serializers.ModelSerializer):
    property = serializers.SerializerMethodField()
    snaktype = serializers.SerializerMethodField()
    datavalue = serializers.SerializerMethodField()
    datatype = serializers.SerializerMethodField()

    def get_snak(self, obj):
        return obj

    def get_property(self, obj):
        snak = self.get_snak(obj)
        return f"P{snak.property.display_id}"

    def get_snaktype(self, obj):
        snak = self.get_snak(obj)
        return snak.get_type_display()

    def get_datavalue(self, obj):
        snak = self.get_snak(obj)
        return snak.value.to_json() if snak.type == 0 else None

    def get_datatype(self, obj):
        snak = self.get_snak(obj)
        return snak.value.get_datatype() if snak.type == 0 else None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Supprime le champ 'datavalue' si snaktype != 'value'
        if ret.get('snaktype') != 'value':
            ret.pop('datavalue', None)
            ret.pop('datatype', None)  # si tu veux aussi retirer datatype
        return ret


class PropertySnakSerializer(BaseSnakSerializer):
    class Meta:
        model = PropertySnak
        fields = ['property', 'snaktype', 'datavalue', 'datatype']


class QualifierSerializer(BaseSnakSerializer):
    def get_snak(self, obj):
        return obj.snak

    class Meta:
        model = Qualifier
        fields = ['property', 'snaktype', 'datavalue', 'datatype']
        list_serializer_class = build_list_serializer(lambda item: item['property'])


class ReferenceSerializer(BaseSnakSerializer):
    def get_snak(self, obj):
        return obj.snak

    class Meta:
        model = ReferenceSnak
        fields = ['property', 'snaktype', 'datavalue', 'datatype']
        list_serializer_class = build_list_serializer(lambda item: item['property'])


class ReferenceRecordSerializer(serializers.ModelSerializer):
    snaks = ReferenceSerializer(many=True)

    class Meta:
        model = ReferenceRecord
        fields = ['snaks']


class StatementSerializer(serializers.ModelSerializer):
    mainsnak = PropertySnakSerializer(required=True)
    qualifiers = QualifierSerializer(many=True)
    references = ReferenceRecordSerializer(many=True, read_only=True, source='reference_records')
    rank = serializers.CharField(source='get_rank_display')

    class Meta:
        model = Statement
        fields = ['mainsnak', 'rank', 'qualifiers', 'references']
        list_serializer_class = build_list_serializer(lambda item: item['mainsnak']['property'])


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    labels = LabelSerializer(many=True, required=False, default=list(), read_only=True)
    descriptions = DescriptionSerializer(many=True, required=False, default=list(), read_only=True)
    aliases = AliasSerializer(many=True, required=False, default=list(), read_only=True)
    claims = StatementSerializer(source='statements', many=True, required=False, read_only=True)
    display_id = serializers.CharField(source='pretty_display_id')
    id = serializers.CharField(source='display_id')

    class Meta:
        model = Item
        fields = ['id', 'display_id', 'labels', 'descriptions', 'aliases', 'claims']

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

        if 'aliases' not in fields:
            self.fields.pop('aliases', None)


class PropertySerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.SlugRelatedField(read_only=True, slug_field='class_name', source='data_type')
    labels = LabelSerializer(many=True, required=False, default=list(), read_only=True)
    descriptions = DescriptionSerializer(many=True, required=False, default=list(), read_only=True)
    aliases = AliasSerializer(many=True, required=False, default=list(), read_only=True)
    display_id = serializers.CharField(source='pretty_display_id')
    id = serializers.CharField(source='display_id')

    class Meta:
        model = Property
        fields = ['id', 'display_id', 'type', 'labels', 'descriptions', 'aliases']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')

        if not request or self.context.get('view').action == 'retrieve':
            self.fields.pop('url', None)
            return

        fields_param = request.query_params.get('fields', '')
        fields = fields_param.split(',') if fields_param else []

        if 'labels' not in fields:
            self.fields.pop('labels', None)

        if 'descriptions' not in fields:
            self.fields.pop('descriptions', None)

        if 'aliases' not in fields:
            self.fields.pop('aliases', None)
