from django import forms
from django.utils.translation import get_language, gettext_lazy as _

import wikibase.models as m
from wikibase.models import ItemMapping, PropertyMapping
from .templatetags import pecunia_tags as tags


def get_instances_of(item):
    return m.Item.objects.filter(statements__mainsnak__property=PropertyMapping.get('is_a'),
                                 statements__mainsnak__value=item)  # TODO: get subclasses

class DocumentTextForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'annotator-text-field', }), label=_('document.text'))

class DocumentMetadataForm(forms.Form):
    title = forms.CharField(label=_('document.title'))
    title_language = forms.ChoiceField(label=_('document.title_language'),
                                       choices=(('en', 'English'), ('fr', 'Français')))
    source_type = forms.ChoiceField(label=_('document.type'))
    author = forms.ChoiceField(label=_('document.author'))
    author_function = forms.ChoiceField(label=_('document.author_function'))
    # date = forms.DateField(label=_('document.date'),
    #                        input_formats=['%Y', ])
    # calendar = forms.ChoiceField(label=_('document.calendar'))
    place = forms.ChoiceField(label=_('document.place'))

    # TODO: Main editions, see also, bibliography

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['source_type'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
                                              m.Item.objects.all()]
        self.fields['author_function'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
                                                  m.Item.objects.all()]
        self.fields['place'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
                                        get_instances_of(ItemMapping.get('place'))]
        self.fields['author'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
                                         get_instances_of(ItemMapping.get('person'))]


class PersonForm(forms.Form):
    name = forms.CharField(label=_('person.name'))
    function = forms.ChoiceField(label=_('person.function'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['function'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
                                           m.Item.objects.all()]
