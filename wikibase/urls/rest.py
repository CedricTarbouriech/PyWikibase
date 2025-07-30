from collections import defaultdict

from rest_framework import routers, serializers, viewsets
from rest_framework.fields import CharField, SerializerMethodField

from wikibase.models import Item, Label, Description, Alias, Statement, PropertySnak, DataValue, StringValue, UrlValue, \
    QuantityValue, TimeValue, GlobeCoordinatesValue, MonolingualTextValue, Qualifier, ReferenceSnak, ReferenceRecord, \
    Property


class PrefixedByLanguageField(serializers.ListSerializer):
    def to_representation(self, data):
        grouped = defaultdict(list)
        for item in super().to_representation(data):
            grouped[item['language']] = item
        return grouped

    def to_internal_value(self, data):
        # data est un dict groupé par langue
        flattened = []
        for lang, values in data.items():
            for value in values:
                flattened.append(value)
        return super().to_internal_value(flattened)


class GroupedByLanguageField(serializers.ListSerializer):
    def to_representation(self, data):
        grouped = defaultdict(list)
        for item in super().to_representation(data):
            grouped[item['language']].append(item)
        return grouped

    def to_internal_value(self, data):
        # data est un dict groupé par langue
        flattened = []
        for lang, values in data.items():
            for value in values:
                flattened.append(value)
        return super().to_internal_value(flattened)


class GroupedByPropertyField(serializers.ListSerializer):
    def to_representation(self, data):
        grouped = defaultdict(list)
        for claim in super().to_representation(data):
            grouped[claim['mainsnak']['property']].append(claim)
        return grouped

    def to_internal_value(self, data):
        # data est un dict groupé par langue
        flattened = []
        for lang, values in data.items():
            for value in values:
                flattened.append(value)
        return super().to_internal_value(flattened)


class GroupedByPropertyField1(serializers.ListSerializer):
    def to_representation(self, data):
        grouped = defaultdict(list)
        for claim in super().to_representation(data):
            grouped[claim['snak']['property']].append(claim['snak'])
        return grouped

    def to_internal_value(self, data):
        # data est un dict groupé par langue
        flattened = []
        for lang, values in data.items():
            for value in values:
                flattened.append(value)
        return super().to_internal_value(flattened)


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


class AliasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alias
        fields = ['language', 'text']
        list_serializer_class = GroupedByLanguageField


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataValue
        fields = []

    def to_representation(self, instance: DataValue):
        value = None
        datatype = None
        if isinstance(instance, StringValue):
            value = {'value': instance.value}
            datatype = 'string'
        elif isinstance(instance, UrlValue):
            value = {'value': instance.value}
            datatype = 'url'
        elif isinstance(instance, QuantityValue):
            value = {'amount': instance.number}
            if instance.lower:
                value['lower'] = instance.lower
            if instance.upper:
                value['upper'] = instance.upper
            if instance.unit:
                value['unit'] = instance.unit.display_id
            datatype = 'quantity'
        elif isinstance(instance, TimeValue):
            value = {
                'time': instance.time,
                'timezone': instance.timezone,
                'precision': instance.precision,
                'after': instance.after,
                'before': instance.before,
                'calendarmodel': instance.calendar_model.display_id
            }
            datatype = 'time'
        elif isinstance(instance, GlobeCoordinatesValue):
            value = {
                'latitude': instance.latitude,
                'longitude': instance.longitude,
                'precision': instance.precision,
                'globe': instance.globe.display_id
            }
            datatype = 'globecoordinate'
        elif isinstance(instance, MonolingualTextValue):
            value = {
                'text': instance.text,
                'language': instance.language
            }
            datatype = 'monolingualtext'
        elif isinstance(instance, Item):
            value = {
                'id': instance.id,
            }
            datatype = 'item'
        return {'value': value, 'type': datatype}


class PropertySnakSerializer(serializers.ModelSerializer):
    snaktype = CharField(source='get_type_display', read_only=True)
    property = SerializerMethodField()
    datavalue = ValueSerializer(source='value', read_only=True)
    datatype = SerializerMethodField()

    class Meta:
        model = PropertySnak
        fields = ['snaktype', 'property', 'datavalue', 'datatype']

    @staticmethod
    def get_property(obj):
        return obj.property.display_id

    @staticmethod
    def get_datatype(obj: PropertySnak):
        return obj.property.data_type.class_name


class QualifierSerializer(serializers.ModelSerializer):
    snak = PropertySnakSerializer()

    class Meta:
        model = Qualifier
        fields = ['snak']


class ReferenceSnakSerializer(serializers.ModelSerializer):
    snak = PropertySnakSerializer()

    class Meta:
        model = ReferenceSnak
        fields = ['snak']
        list_serializer_class = GroupedByPropertyField1


class ReferenceRecordSerializer(serializers.ModelSerializer):
    snaks = ReferenceSnakSerializer(many=True)

    class Meta:
        model = ReferenceRecord
        fields = ['snaks']
        list_serializer_class = GroupedByPropertyField1


class StatementSerializer(serializers.ModelSerializer):
    mainsnak = PropertySnakSerializer()
    rank = CharField(source='get_rank_display', read_only=True)
    qualifiers = QualifierSerializer(many=True)
    references = ReferenceRecordSerializer(many=True, source='reference_records')

    class Meta:
        model = Statement
        fields = ['mainsnak', 'qualifiers', 'rank', 'references']
        list_serializer_class = GroupedByPropertyField


class ItemSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, required=False, default=list())
    descriptions = DescriptionSerializer(many=True, required=False, default=list())
    aliases = AliasesSerializer(many=True, required=False, default=list())
    claims = StatementSerializer(many=True, source='statements', required=False, default=list())

    class Meta:
        model = Item
        fields = ['display_id', 'labels', 'descriptions', 'aliases', 'claims']

    def create(self, validated_data):
        print(validated_data)
        item = Item.objects.create(**validated_data)
        # Labels
        print(type(validated_data['labels']), validated_data['labels'])
        for label in validated_data['labels']:
            item.set_label(label['language'], label['text'])
        return Item.objects.create(**validated_data)

    def update(self, instance, validated_data):
        print(type(instance), instance)
        print("oui2")
        return super().update(instance, validated_data)


# ViewSets define the view behavior.
class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'display_id'


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'display_id'


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'properties', PropertyViewSet)
