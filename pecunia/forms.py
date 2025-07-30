from django import forms
from django.utils.translation import gettext_lazy, get_language

import wikibase.models as m
from .templatetags import pecunia_tags as tags


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
