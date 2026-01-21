import sys

from django.db import migrations

from pecunia.models import Datatype, Property, Item, PropertyMapping, ItemMapping, PropertySnak, Statement, \
    PropertyOrderPreference


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


def set_property_order_list(item, properties):
    PropertyOrderPreference.objects.bulk_create([PropertyOrderPreference(item=item, prop=prop, ordering=i + 1) for i, prop in enumerate(properties)])

def populate_db(apps, *_ignored):
    prop_is_a = create_property('is a', 'nature of the item (what is this item?)', 'Item')
    create_property('subclass of', 'X subclass of Y: every instance of X is an instance of Y', 'Item')
    prop_date = create_property('date', 'date when an event happened', 'TimeValue')
    create_property('earliest date', 'earliest date at which an event could have happened', 'TimeValue')
    create_property('latest date', 'latest date at which an event could have happened', 'TimeValue')
    create_property('during', 'the process occurred during another process', 'Item')

    ## Relatif à l’épistémologie
    create_property('passage', 'token id', 'StringValue')
    create_property('asserted in', 'document in which a statement is asserted', 'Item')
    create_property('hypothesided from text', '', 'Item')
    create_property('hypothesided from statement', '', 'StatementValue') # FIXME Vérifier StatementValue

    # Propriétés des documents
    ##
    prop_title = create_property('title', 'title of a document', 'MonolingualTextValue')
    prop_source_type = create_property('type of source', 'epigraphic/papyrological/literary/legal compilations', 'Item')  # Epigraphique, Papyrologique, Littéraire
    prop_text_type = create_property('type of text', 'decree/edict', 'Item')  # Decree, Edict, etc.
    prop_lang = create_property('lang', 'language of the text', 'Item')
    prop_text = create_property('text', 'text of the document', 'StringValue')
    prop_author = create_property('author', 'person (natural or civic body or association) who wrote the text', 'Item')
    prop_author_role = create_property('role of the author', 'role of the author when they wrote the text (only used if natural person)', 'Item') # TODO Add constraint of exclusivity with is_a civic_body ou is_a association
    create_property('English translation', 'English translation of the text', 'StringValue')
    prop_prov = create_property('provenance', 'place from where the document originates', 'Item')
    # - date de composition : utiliser date.

    ## Références et bibliographie
    prop_see_also = create_property('see also', 'online edition of the text', 'UrlValue')
    prop_main_ed = create_property('main edition', 'edition giving the most recent and best version of the text', 'UrlValue')
    prop_biblio = create_property('bibliography', 'scientific publication discussing the text', 'UrlValue')
    create_property('link label', 'label used to nicely display the link, instead of the url', 'StringValue') # Qualifier d’un lien TODO Ajouter contrainte
    prop_commentary = create_property('commentary', 'commentary of the historian adding the text', 'StringValue')

    # Propriété pour les lieux
    create_property('ancient name', 'name of a place used in Roman empire', 'MonolingualTextValue')
    prop_coords = create_property('coordinates', 'coordinates of the place on Earth', 'GlobeCoordinatesValue')
    prop_part_of = create_property('part of', 'object the subject is a part of', 'Item')  # TODO Expliquez ça dans le guide d’annotations
    prop_pleiades_link = create_property('Pleiades link', 'link to the Pleiades page about the subject', 'UrlValue')
    create_property('Trismegistos link', 'link to the Trismegistos page about the subject', 'UrlValue')
    prop_size = create_property('size', 'estimated size of the city', 'Item')
    # Statut : utiliser is_a

    # Propriétés pour les personnes physiques
    # Pour les noms, utiliser les labels ?
    create_property('sex', 'male/female', 'Item')
    create_property('legal status', 'status of a person', 'Item')  # Esclave, Affranchi, Libre
    create_property('citizenship', 'city of origin', 'Item')  # Cité de rattachement : origo
    prop_civic_status = create_property('civic status', 'peregrinus/Roman', 'Item')
    # Si esclave pas de civic status ni citizenship
    prop_social_level = create_property('social level', 'estimated social level of the person', 'Item')
    create_property('public function', 'public function (civic or military) of the subject', 'Item') # Fonctions publiques civiles et militaires -> détenteur d’un pouvoir public
    create_property('occupation', 'job of the subject', 'Item') # Métiers
    create_property('member of', 'group or institution the subject is a member of', 'Item')

    # Process -> Expression
    # Personne -[|-> Expression]> Process
    create_property('described as', 'expression used to describe something (e.g. a person or a process)', 'Item')
    create_property('described by', 'the person describing the subject', 'Item')

    create_property('ruled as', 'expression used to', 'Item') # Pour les décisions de justice
    create_property('ruled by', 'the person taking a decision about the subject', 'Item')

    # Utiliser propriété Trismegistos link

    # Propriétés pour les personnes morales (civic body or association)
    ## Propriétés pour les conseils, les assemblées, les associations, les groupements semi-publics
    create_property('territorial jurisdiction', 'place where the entity has legal power', 'Item')
    create_property('estimated size', 'estimated number of members', 'QuantityValue')
    create_property('recruitment process', 'how people can become members', 'Item')

    # Propriétés pour les ressources
    # Pour les noms, utiliser les labels

    # Propriétés pour les processus
    prop_place = create_property('place', 'place where the event took place', 'Item')
    create_property('quantity', 'quantity of the benefit', 'QuantityValue')
    create_property('unit', 'unit of the benefit', 'Item')
    prop_benefit = create_property('benefit', 'resource obtained through the process', 'Item')
    prop_beneficiary = create_property('beneficiary', 'person obtaining the benefit', 'Item')
    prop_provider = create_property('provider', 'person giving the benefit', 'Item')
    # FIXME broker = participant au processus sans qui le processus ne pourrait avoir lieu
    create_property('role in a process', 'role (function/occupation) of the person explaining why they are involved in the process', 'Item')

    # Propriétés pour les fonctions ou les titres
    create_property('administrative level', '', 'Item')  # Infra-civic / civic / provincial / emperor / army TODO Mettre dans la description
    create_property('is mentioned in', 'document in which an entity is mentioned', 'Item')
    create_property('capital of an endowment', 'capital first invested in the endowment', 'QuantityValue')
    create_property('percentage extracted from a capital', 'known or estimated rate of interest', 'QuantityValue')
    create_property('process manner', 'adverb to describe a process', 'Item')
    create_property('remainder of', 'remaining resource after some part of it has been used', 'Item')

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
    create_property_mapping('coordinates', prop_coords)
    create_property_mapping('pleiades', prop_pleiades_link)

    higher_type = create_item('type', 'higher type')
    item_document = create_item('document', '')
    item_person = create_item('person', '')
    item_place = create_item('place', '')
    resource = create_item('resource', '')
    item_process = create_item('benefit process', '')

    is_a(item_document, higher_type)
    is_a(item_person, higher_type)
    is_a(item_place, higher_type)
    is_a(resource, higher_type)
    is_a(item_process, higher_type)

    create_item_mapping('type', higher_type)
    create_item_mapping('document', item_document)
    create_item_mapping('person', item_person)
    create_item_mapping('place', item_place)
    create_item_mapping('resource', resource)
    create_item_mapping('process', item_process)
    create_item_mapping('calendar', create_item('calendar', ''))
    create_item_mapping('earth', create_item('Earth', ''))

    item_source_type = create_item('type of source', '')
    item_epi = create_item('epigraphic', '')
    item_papy = create_item('papyrological', '')
    item_lit = create_item('literary', '')
    item_leg_comp = create_item('legal compilations', 'digest, Codex Theodosianus')

    is_a(item_epi, item_source_type)
    is_a(item_papy, item_source_type)
    is_a(item_lit, item_source_type)
    is_a(item_leg_comp, item_source_type)

    item_text_type = create_item('type of text', '')

    item_dedication = create_item('dedication', '')
    is_a(item_dedication, item_text_type)
    item_building_dedi = create_item('dedication of building', '')
    is_a(item_building_dedi, item_dedication)
    item_endowment_dedi = create_item('dedication of a endowment', '')
    is_a(item_endowment_dedi, item_dedication)

    item_honorific = create_item('honorific', '')
    is_a(item_honorific, item_text_type)
    item_emperor_honorific = create_item('honorific for an emperor', '')
    is_a(item_emperor_honorific, item_honorific)
    item_governor_honorific = create_item('honorific for a governor', '')
    is_a(item_governor_honorific, item_honorific)
    item_civic_honorific = create_item('honorific for a civic official', '')
    is_a(item_civic_honorific, item_honorific)

    is_a(create_item('edict', ''), item_text_type)

    item_decree = create_item('decree', '')
    is_a(item_decree, item_text_type)
    is_a(create_item('consolatory decree', ''), item_decree)
    is_a(create_item('honorific decree', ''), item_decree)

    is_a(create_item('rescript', ''), item_text_type)
    is_a(create_item('graffito', ''), item_text_type)
    is_a(create_item('funerary', ''), item_text_type)
    is_a(create_item('municipal charter', ''), item_text_type)
    is_a(create_item('votive', ''), item_text_type)
    is_a(create_item('petition', ''), item_text_type)
    is_a(create_item('juristic excerpt', ''), item_text_type)

    is_a(create_item('historical narrative', ''), item_text_type)
    is_a(create_item('encomiastic literature', ''), item_text_type)
    is_a(create_item('apologetic literature', ''), item_text_type)
    is_a(create_item('philosophical discourse', ''), item_text_type)
    is_a(create_item('technical literature', ''), item_text_type)
    is_a(create_item('official correspondence', ''), item_text_type)
    is_a(create_item('epistolary literature', ''), item_text_type)

    item_lang = create_item('language', '')
    item_ancient_greek = create_item('Ancient greek', '')
    is_a(item_ancient_greek, item_lang)
    item_latin = create_item('Latin', '')
    is_a(item_latin, item_lang)

    create_item_mapping('grc', item_ancient_greek)
    create_item_mapping('la', item_latin)

    item_role = create_item('role', '')

    # role privé = occupation, role public = fonction
    item_private = create_item('private role', '') #TODO Expliciter dans le guide d’annotation + Mettre en place un processus de controle des roles créés
    item_semi_public = create_item('semi-public role', '')
    item_public = create_item('public role', '')

    item_individual = create_item('individual role', 'role for a natural person')
    item_corporate = create_item('corporate body role', 'role for a civic group or an association')

    item_roman_role = create_item('Roman role', 'official function in western cities')
    item_greek_role = create_item('Greek role', 'official function in eastern cities')

    is_a(item_private, item_role)
    is_a(item_semi_public, item_role)
    is_a(item_public, item_role)
    is_a(item_individual, item_role)
    is_a(item_corporate, item_role)

    item_place_size = create_item('size of a place', '')
    is_a(create_item('small', 'size of a place'), item_place_size)
    is_a(create_item('medium', 'size of a place'), item_place_size)
    is_a(create_item('large', 'size of a place'), item_place_size)
    is_a(create_item('very large', 'size of a place'), item_place_size)

    # TODO Gérer l’empire et l’Italie (qui n’est pas une province)
    create_item('province', '')
    create_item('city', '')
    create_item('Roman colony', '')
    create_item('municipium', '')
    create_item('non-Roman city', '')
    create_item('Egyptian nome', '')
    create_item('nome capital', '')
    create_item('village', '')

    social_level = create_item('social level', '')
    social_level_1 = create_item('social level 1 - top family',
                                 'such as ancestors belonging to the first in the city of Aphrodisias')
    social_level_1p = create_item('social level 1+',
                                  'such as M. Ulpius Carminius Claudianus Claudianus at Aphrodisias (convergence of political importance + able of giving 100000 of denarii)')
    social_level_2 = create_item('social level 2', 'such as top family, and sculptor in Aphrodisias')
    social_level_3 = create_item('social level 3', 'such as plain boulettes/senator in the city, minor official functions')
    social_level_4 = create_item('social level 4', 'working person, owner of shop, professional activity belonging top upper level of the plebs')
    social_level_5 = create_item('social level 5', 'the 90%')

    is_a(social_level_1, social_level)
    is_a(social_level_1p, social_level)
    is_a(social_level_2, social_level)
    is_a(social_level_3, social_level)
    is_a(social_level_4, social_level)
    is_a(social_level_5, social_level)

    item_sex = create_item('sex', '')
    is_a(create_item('male', 'sex'), item_sex)
    is_a(create_item('female', 'sex'), item_sex)

    item_legal_status = create_item('legal status', '')
    is_a(create_item('enslaved person', 'legal status'), item_legal_status)
    is_a(create_item('freed person', 'legal status'), item_legal_status)
    is_a(create_item('freeborn', 'legal status'), item_legal_status)

    item_civic_status = create_item('civic status', '')
    is_a(create_item('peregrinus', 'civic status'), item_civic_status)
    is_a(create_item('Roman', 'civic status'), item_civic_status)

    item_recruitment_process = create_item('recruitment process', 'how people can become members')
    is_a(create_item('elected', 'recruitment process'), item_recruitment_process)
    is_a(create_item('drawn by lots', 'recruitment process'), item_recruitment_process)
    is_a(create_item('designated', 'recruitment process'), item_recruitment_process)
    is_a(create_item('property qualification', 'recruitment process'), item_recruitment_process)
    is_a(create_item('by birth', 'recruitment process'), item_recruitment_process)

    item_administrative_level = create_item('administrative level', '')
    is_a(create_item('infra-civic', ''), item_administrative_level)
    is_a(create_item('civic', ''), item_administrative_level)
    is_a(create_item('provincial', ''), item_administrative_level)
    # is_a(create_item('emperor', ''), item_administrative_level) TODO C’est pas un niveau, c’est le titre lui-même (voir pb avec Empire et Italie)
    is_a(create_item('army', ''), item_administrative_level)

    item_editing_role = create_item('editing role', '')
    is_a(create_item('author', ''), item_editing_role)
    is_a(create_item('reviewer', ''), item_editing_role)

    set_property_order_list(item_document, [prop_title, prop_is_a, prop_source_type, prop_text_type, prop_prov, prop_date, prop_text, prop_author, prop_biblio])
    set_property_order_list(item_person, [prop_is_a, #prop_place,
                                           prop_social_level, prop_see_also])
    set_property_order_list(item_place, [prop_is_a, prop_coords, prop_part_of, prop_civic_status, prop_pleiades_link, prop_size,
                                         #prop_mentioned_in
                                         ])
    set_property_order_list(item_process, [prop_is_a, #prop_mentioned_in,
        prop_date, prop_place, prop_beneficiary, prop_benefit, prop_provider, ])#TODO prop_broker

class Migration(migrations.Migration):
    dependencies = [
        ('pecunia', '0002_populate'),
    ]

    operations = [
        migrations.RunPython(populate_db),
    ] if 'test' not in sys.argv else []  # The migration is not applied for unit testing.
