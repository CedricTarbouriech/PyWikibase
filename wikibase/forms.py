from django import forms
from django.utils.translation import gettext_lazy, get_language

import wikibase.models as m
from pecunia.templatetags import pecunia_tags as tags


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
                                       m.Item.objects.all()]


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
