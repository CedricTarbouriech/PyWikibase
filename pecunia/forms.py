from django import forms
from django.utils.translation import gettext_lazy, get_language

from .templatetags import pecunia_tags as tags
import wikibase.models as m


def get_instances_of(item):
    return m.Item.objects.filter(
        statement__mainsnak__value=item)  # TODO: get subclasses


class DocumentForm(forms.Form):
    title = forms.CharField(label=gettext_lazy('document.title'))
    title_language = forms.ChoiceField(label=gettext_lazy('document.title_language'),
                                       choices=(('en', 'English'), ('fr', 'Français')))
    source_type = forms.ChoiceField(label=gettext_lazy('document.type'))
    # function_type = forms.ChoiceField(label=gettext_lazy('document.function'))
    author = forms.ChoiceField(label=gettext_lazy('document.author'))
    author_function = forms.ChoiceField(label=gettext_lazy('document.author_function'))
    # date = forms.CharField(label=gettext_lazy('document.date'))  # FIXME after implementing date
    # calendar = forms.ChoiceField(label=gettext_lazy('document.calendar'))
    # language = forms.ChoiceField(label=gettext_lazy('document.language'),
    #                              choices=(('grc', 'Ancient greek'), ('la', 'Latin')))  # TODO: use items
    place = forms.ChoiceField(label=gettext_lazy('document.place'))

    # TODO: Main editions, see also, bibliography

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    #     self.fields['title_language'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
    #                                              get_instances_of(m.Item.objects.get(display_id=19))]
    #     self.fields['source_type'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
    #                                           get_instances_of(m.Item.objects.get(display_id=12))]
    #     self.fields['language'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
    #                                        get_instances_of(m.Item.objects.get(display_id=18))]
    #     self.fields['function_type'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
    #                                             m.Item.objects.all()]
    #     self.fields['author_function'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
    #                                               m.Item.objects.all()]
    #     self.fields['translation_language'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
    #                                                    m.Item.objects.all()]
    #     self.fields['place'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
    #                                     get_instances_of(m.Item.objects.get(display_id=3))]
        self.fields['author'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
                                         m.Item.objects.all()]


class PersonForm(forms.Form):
    name = forms.CharField(label=gettext_lazy('person.name'))
    function = forms.ChoiceField(label=gettext_lazy('person.function'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['function'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
                                           m.Item.objects.all()]


class ItemLabelDescriptionForm(forms.Form):
    language = forms.ChoiceField(label=gettext_lazy('global.language'),
                                 choices=(('en', 'English'), ('fr', 'Français')))  # TODO: trad
    label = forms.CharField(label=gettext_lazy('form.entity.label'), strip=True)
    description = forms.CharField(label=gettext_lazy('form.entity.description'),
                                  widget=forms.TextInput(attrs={'size': 80}), strip=True, required=False)

    def __init__(self, *args, **kwargs):
        display_id = kwargs.pop('display_id', None)
        super(ItemLabelDescriptionForm, self).__init__(*args, **kwargs)
        if display_id:
            self.fields['language'].disabled = True


class StatementUpdateForm(forms.Form):
    type = forms.ChoiceField(label=gettext_lazy('statement.type'),
                             choices=(('value', 'Value'),
                                      ('somevalue', 'Some value'),
                                      ('novalue', 'No value')))


class StringStatementUpdateForm(StatementUpdateForm):
    value = forms.CharField(widget=forms.Textarea)


class MonolingualTextStatementUpdateForm(StatementUpdateForm):
    language = forms.ChoiceField(label=gettext_lazy('global.language'), choices=(
        ('en', 'English'), ('fr', 'Français'), ('la', 'Latin'), ('grc', 'Ancient greek')))
    value = forms.CharField(widget=forms.Textarea)


class ItemStatementUpdateForm(StatementUpdateForm):
    item = forms.ChoiceField(label=gettext_lazy('global.entity'), choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
                                       m.Item.objects.all()]  # FIXME: language code


class StatementCreateForm(forms.Form):
    property = forms.ChoiceField(label=gettext_lazy('global.property'), choices=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property'].choices = [(x.display_id, tags.label_or_default(x, get_language())) for x in
                                           m.Property.objects.all()]


class PropertyLabelDescriptionForm(forms.Form):
    language = forms.ChoiceField(label=gettext_lazy('global.language'),
                                 choices=(('en', 'English'), ('fr', 'Français')))  # TODO: trad
    label = forms.CharField(label=gettext_lazy('form.entity.label'), strip=True)
    description = forms.CharField(label=gettext_lazy('form.entity.description'),
                                  widget=forms.TextInput(attrs={'size': 80}), strip=True, required=False)
    type = forms.ChoiceField(label=gettext_lazy('form.property.type'),
                             choices=(
                                 ("Item", 'Item'),
                                 ("Property", 'Property'),
                                 ("StringValue", 'String'),
                                 ("UrlValue", 'URL'),
                                 ("QuantityValue", 'Quantity'),
                                 ("TimeValue", 'Time'),
                                 ("GlobeCoordinatesValue", 'Globe coordinates'),
                                 ("MonolingualTextValue", 'Monolingual string')
                             ))

    def __init__(self, *args, **kwargs):
        display_id = kwargs.pop('display_id', None)
        super(PropertyLabelDescriptionForm, self).__init__(*args, **kwargs)
        if display_id:
            self.fields['language'].disabled = True
            self.fields['type'].disabled = True

    """string OK
    coordo OK
    texte monolingue OK
    élément OK
    propriété OK
    quantité OK
    url OK
    
    point dans le temps
    
    données tab
    edtf
    expression math
    fichier commons
    identifiant externe
    notation musicale
    schéma
    """
