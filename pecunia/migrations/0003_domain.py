from django.db import migrations

from pecunia.models import Datatype, Property, Item, PropertyMapping, ItemMapping, PropertySnak, Statement


def create_property(label, description, datatype):
    prop = Property.objects.create(data_type=Datatype.objects.get(class_name=datatype))
    prop.set_label('en', label)
    if description:
        prop.set_description('en', description)
    prop.save()
    return prop

def is_a(item1, item2):
    snak = PropertySnak.objects.create(property=PropertyMapping.get('is_a'), type=PropertySnak.Type.VALUE,
                                       value=item2)
    Statement.objects.create(subject=item1, mainsnak=snak, rank=Statement.Rank.NORMAL)


def create_property_mapping(key, prop):
    PropertyMapping.objects.create(key=key, property=prop)


def create_item(label, description):
    item = Item.objects.create()
    item.set_label('en', label)
    if description:
        item.set_description('en', description)
    item.save()
    return item


def create_item_mapping(key, item):
    ItemMapping.objects.create(key=key, item=item)


def populate_db(apps, *_ignored):
    prop_is_a = create_property('is a', '', 'Item')
    create_property('subclass', '', 'Item')
    prop_date = create_property('date', 'date when an event occured', 'TimeValue')
    create_property('date (reign)', '', 'Item')
    ## Relatif à l’épistémologie
    # TODO create_property('') explicite / implicite (écrit dans le texte / interprété par les historiens)

    # 54 BCE - 58 (CE)?
    # 15/03/44 BCE - 14/06/44 (CE)?

    # Propriétés des documents
    ##
    prop_title = create_property('title', '', 'MonolingualTextValue')
    prop_source_type = create_property('type of source', '', 'Item')  # Epigraphique, Papyrologique, Littéraire
    create_property('type of text', '', 'Item')  # Decree, Edict, etc.
    prop_lang = create_property('lang', '', 'Item')
    prop_text = create_property('text', '', 'StringValue')
    prop_author = create_property('author', 'person (natural or civic body or association) who wrote the text', 'Item')
    prop_author_role = create_property('role of the author', 'role of the author when they wrote the text', 'Item')
    create_property('English translation', 'English translation of the text', 'StringValue')
    prop_prov = create_property('provenance', 'place from where the document originates', 'Item')
    # - date de composition : utiliser date.
    ## Références et bibliographie
    prop_main_ed = create_property('main edition', '', 'Item')
    prop_see_also = create_property('see also', 'online edition of the text', 'UrlValue')
    prop_biblio = create_property('bibliography', 'scientific publication discussing the text', 'Item')
    prop_commentary = create_property('commentary', '', 'StringValue')

    # Propriété pour les lieux
    create_property('ancient name', '', 'MonolingualTextValue')
    create_property('coordinates', '', 'GlobeCoordinatesValue')
    create_property('part of', '', 'Item')  # Expliquez ça dans le guide d’annotations
    create_property('Pleiades link', '', 'UrlValue')
    create_property('Trismegistos link', '', 'UrlValue')
    create_property('size', '', 'Item')
    # Statut : utiliser is_a

    # Propriétés pour les personnes physiques
    # Pour les noms, utiliser les labels ?
    create_property('sex', '', 'Item')
    create_property('legal status', '', 'Item')  # Esclave, Affranchi, Libre
    create_property('citizenship', '', 'Item')  # Cité de rattachement : origo
    create_property('civic status', 'foreigner/Latin/Roman', 'Item')
    # Si esclave pas de civic status ni citizenship
    create_property('social level', '', 'Item')
    create_property('function', '', 'Item')
    create_property('member of', '', 'Item')
    create_property('recognised as', 'quality/? attributed to the person by someone else',
                    'Item')  # FIXME Voir avec Elizabeth pour les qualités négatives
    # Utiliser propriété Trismegistos link

    # Propriétés pour les personnes morales (civic body or association)
    ## Propriétés pour les conseils, les assemblées, les associations, les groupements semi-publics
    create_property('territorial jurisdiction', 'place where the entity has legal power', 'Item')
    create_property('estimated size', 'estimated number of members', 'QuantityValue')
    create_property('recruitment process', 'how people can become members', 'Item')

    # Propriétés pour les ressources
    # Pour les noms, utiliser les labels

    # Propriétés pour les processus
    create_property('place', 'place where the event took place', 'Item')
    create_property('legality', 'is the process legal?', 'Item')
    create_property('challenged by', 'person who challenged the process', 'Item')
    create_property('challenge type', '', 'Item')  # judiciairement, moralement
    create_property('quantity', '', 'QuantityValue')
    create_property('unit', '', 'Item')
    create_property('benefit', 'resource obtained through the process', 'Item')  # FIXME check description
    create_property('beneficiary', '', 'Item')
    create_property('provider', '', 'Item')
    # FIXME broker
    create_property('function', '', 'Item')

    # Propriétés pour les fonctions ou les titres
    create_property('administrative level', '', 'Item')  # Infra-civic / civic / provincial / empire / emperor / army
    create_property('Greek or Roman position', '', 'Item')  # Greek or Roman position FIXME Is a ?

    # Propriétés pour les ouvrages bibliographiques
    create_property('zotero link', '', 'UrlValue')

    # À trier
    create_property('certainty degree', '', 'Item')
    create_property('is mentioned in', 'document in which an entity is mentioned', 'Item')
    create_property('capital of an endowment', '', 'QuantityValue')
    create_property('percentage extracted from a capital', '', 'QuantityValue')
    create_property('edited by', 'user who edited the document', 'UserValue')
    create_property('editing role', '', 'Item')

    create_property_mapping('is_a', prop_is_a)
    create_property_mapping('date', prop_date)
    create_property_mapping('title', prop_title)
    create_property_mapping('source_type', prop_source_type)
    create_property_mapping('language', prop_lang)
    create_property_mapping('text', prop_text)
    create_property_mapping('author', prop_author)
    create_property_mapping('author_function', prop_author_role)
    create_property_mapping('main_edition', prop_main_ed)
    create_property_mapping('see_also', prop_see_also)
    create_property_mapping('bibliography', prop_biblio)
    create_property_mapping('commentary', prop_commentary)
    create_property_mapping('provenance', prop_prov)

    create_item_mapping('document', create_item('document', ''))
    create_item_mapping('person', create_item('person', ''))
    create_item_mapping('place', create_item('place', ''))
    create_item_mapping('resource', create_item('resource', ''))
    create_item_mapping('process', create_item('benefit process', ''))
    create_item_mapping('calendar', create_item('calendar', ''))
    create_item_mapping('earth', create_item('Earth', ''))

    social_level = create_item('social level', '')
    social_level_1 = create_item('social level 1 - top family', 'such as ancestors belonging to the first in the city of Aphrodisias')
    social_level_1p = create_item('social level 1+', 'such as M. Ulpius Carminius Claudianus Claudianus at Aphrodisias (convergence of political importance + able of giving 100000 of denarii)')
    social_level_2 = create_item('social level 2', 'such as top family, and sculptor in Aphrodisias')

    is_a(social_level_1, social_level)
    is_a(social_level_1p, social_level)
    is_a(social_level_2, social_level)

class Migration(migrations.Migration):
    dependencies = [
        ('pecunia', '0002_populate'),
    ]

    operations = [
        migrations.RunPython(populate_db),
    ]
