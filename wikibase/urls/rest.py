from collections import defaultdict

from rest_framework import routers, serializers, viewsets
from rest_framework.fields import CharField, SerializerMethodField

from wikibase.models import Item, Label, Description, Alias, Statement, PropertySnak, DataValue, StringValue, UrlValue, \
    QuantityValue, TimeValue, GlobeCoordinatesValue, MonolingualTextValue, Qualifier, ReferenceSnak, ReferenceRecord, \
    Property


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['language', 'text']


class DescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Description
        fields = ['language', 'text']


class AliasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alias
        fields = ['language', 'text']


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


class ReferenceRecordSerializer(serializers.ModelSerializer):
    snaks = ReferenceSnakSerializer(many=True)

    class Meta:
        model = ReferenceRecord
        fields = ['snaks']

    def to_representation(self, instance: ReferenceRecord):
        rep = super().to_representation(instance)
        grouped = defaultdict(list)
        for claim in rep['snaks']:
            grouped[claim['snak']['property']].append(claim['snak'])
        rep['snaks'] = grouped
        return rep


class StatementSerializer(serializers.ModelSerializer):
    mainsnak = PropertySnakSerializer()
    rank = CharField(source='get_rank_display', read_only=True)
    qualifiers = QualifierSerializer(many=True)
    references = ReferenceRecordSerializer(many=True, source='reference_records')

    class Meta:
        model = Statement
        fields = ['mainsnak', 'qualifiers', 'rank', 'references']

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Group claims by property
        grouped = defaultdict(list)
        for claim in rep['qualifiers']:
            grouped[claim['snak']['property']].append(claim['snak'])
        rep['qualifiers'] = grouped

        return rep


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    labels = LabelSerializer(many=True)
    descriptions = DescriptionSerializer(many=True)
    aliases = AliasesSerializer(many=True)
    claims = StatementSerializer(many=True, source='statements')

    class Meta:
        model = Item
        fields = ['display_id', 'labels', 'descriptions', 'aliases', 'claims']

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Group labels by language
        grouped = defaultdict(dict)
        for label in rep['labels']:
            grouped[label['language']] = label

        rep['labels'] = grouped

        # Group descriptions by language
        grouped = defaultdict(dict)
        for description in rep['descriptions']:
            grouped[description['language']] = description

        rep['descriptions'] = grouped

        # Group aliases by language
        grouped = defaultdict(list)
        for alias in rep['aliases']:
            grouped[alias['language']].append({
                'language': alias['language'],
                'value': alias['value']
            })
        rep['aliases'] = grouped

        # Group claims by property
        grouped = defaultdict(list)
        for claim in rep['claims']:
            grouped[claim['mainsnak']['property']].append(claim)
        rep['claims'] = grouped

        return rep


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
