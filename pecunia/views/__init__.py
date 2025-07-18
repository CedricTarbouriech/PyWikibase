from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, FormView, DetailView

from wikibase import api as wbapi, models as m
from .document_views import DocumentDashboard, DocumentDisplay, DocumentCreation, DocumentUpdate, DocumentDelete
from .person_views import PersonDashboard, PersonDisplay, PersonCreation, PersonUpdate, PersonDelete
from .place_views import PlaceDashboard, PlaceDisplay, PlaceCreation, PlaceUpdate, PlaceDelete
from ..forms import ItemLabelDescriptionForm, PropertyLabelDescriptionForm

DEFAULT_PAGINATOR_LIMIT = 25


class Home(TemplateView):
    template_name = 'pecunia/index.html'


class ModelDashboardView(TemplateView):
    model = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.model.objects.all()
        paginator = Paginator(items,
                              self.request.GET.get("limit") or DEFAULT_PAGINATOR_LIMIT)  # Show 25 contacts per page.

        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context


class ItemDashboard(ModelDashboardView):
    template_name = 'pecunia/item_list.html'
    model = m.Item


class ItemDisplay(TemplateView):
    template_name = 'pecunia/item_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        item = m.Item.objects.get(display_id=self.kwargs['display_id'])
        context['item'] = item

        props = set()
        for statement_prop in item.statement_set.all():
            props.add(statement_prop.mainSnak.propertysnak.property)

        statements = []
        for prop in props:
            values = []
            for statement in item.statement_set.filter(mainSnak__propertysnak__property=prop):
                values.append(statement)
            statements.append((prop, values))
        context['statements'] = statements

        linked_items = []
        for stmt in m.Statement.objects.filter(mainSnak__propertysnak__propertyvaluesnak__value=item):
            linked_items.append(stmt.subject.display_id)
        context['linked_items'] = sorted(linked_items)
        return context


class ItemUpdateLabelDescription(LoginRequiredMixin, FormView):
    template_name = 'pecunia/item_update_labeldescription.html'
    form_class = ItemLabelDescriptionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        display_id = self.kwargs['display_id']
        lang = self.kwargs['lang']
        item = m.Item.objects.get(display_id=display_id)
        kwargs['display_id'] = display_id
        kwargs['initial']['language'] = lang
        try:
            label = item.labels.monolingualtextvalue_set.get(lang_code=lang)
            kwargs['initial']['label'] = label.value
        except ObjectDoesNotExist:
            pass
        try:
            description = item.descriptions.monolingualtextvalue_set.get(lang_code=lang)
            kwargs['initial']['description'] = description.value
        except ObjectDoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            item = m.Item.objects.get(display_id=self.kwargs['display_id'])
            language_code = self.kwargs['lang']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            wbapi.add_label(item, language_code, label)
            wbapi.add_description(item, language_code, description)
            self.kwargs['display_id'] = item.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('item_display', kwargs={'display_id': self.kwargs['display_id']})


class ItemCreation(LoginRequiredMixin, FormView):
    template_name = 'pecunia/item_creation.html'
    form_class = ItemLabelDescriptionForm

    def form_valid(self, form):
        if form.is_valid():
            # Creation of the property
            item = wbapi.create_item()
            self.kwargs['display_id'] = item.display_id

            # Creation of the label and the description
            language_code = form.cleaned_data['language']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            wbapi.add_label(item, language_code, label)
            wbapi.add_description(item, language_code, description)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('item_display', kwargs=self.kwargs)


class ItemDelete(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/confirm_delete.html'
    success_url = reverse_lazy('item_list')

    def post(self, request, *args, **kwargs):
        if "confirm" in request.POST:
            m.Item.objects.get(display_id=self.kwargs['display_id']).delete()
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = f"Item Q{self.kwargs['display_id']}"
        return context


class PropertyDashboard(ModelDashboardView):
    template_name = 'pecunia/property_list.html'
    model = m.Property


class PropertyDisplay(DetailView):
    template_name = 'pecunia/property_detail.html'

    def get_object(self, queryset=None):
        return m.Property.objects.get(display_id=self.kwargs['display_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            prop = kwargs['object']
            stmts = m.Statement.objects.filter(mainSnak__propertysnak__property=prop)
            linked_items = []
            for stmt in stmts:
                linked_items.append(stmt.subject.display_id)
            context['linked_items'] = sorted(linked_items)
        except ObjectDoesNotExist as e:
            raise Http404 from e

        return context


class PropertyCreation(LoginRequiredMixin, FormView):
    template_name = 'pecunia/property_creation.html'
    form_class = PropertyLabelDescriptionForm

    def form_valid(self, form):
        if form.is_valid():
            # Creation of the property
            datatype = form.cleaned_data['type']
            prop = wbapi.create_property(datatype=m.Datatype.objects.get(class_name=datatype))
            self.kwargs['display_id'] = prop.display_id

            # Creation of the label and the description
            language_code = form.cleaned_data['language']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            wbapi.add_label(prop, language_code, label)
            wbapi.add_description(prop, language_code, description)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('property_display', kwargs=self.kwargs)


class PropertyUpdateLabelDescription(LoginRequiredMixin, FormView):
    template_name = 'pecunia/property_update_labeldescription.html'
    form_class = PropertyLabelDescriptionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        display_id = self.kwargs['display_id']
        lang = self.kwargs['lang']
        prop = m.Property.objects.get(display_id=display_id)
        kwargs['display_id'] = display_id
        kwargs['initial']['language'] = lang
        kwargs['initial']['type'] = prop.data_type.class_name
        try:
            label = prop.labels.monolingualtextvalue_set.get(lang_code=lang)
            kwargs['initial']['label'] = label.value
        except ObjectDoesNotExist:
            pass
        try:
            description = prop.descriptions.monolingualtextvalue_set.get(lang_code=lang)
            kwargs['initial']['description'] = description.value
        except ObjectDoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            prop = m.Property.objects.get(display_id=self.kwargs['display_id'])
            language_code = self.kwargs['lang']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            wbapi.add_label(prop, language_code, label)
            wbapi.add_description(prop, language_code, description)
            self.kwargs['display_id'] = prop.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('property_display', kwargs={'display_id': self.kwargs['display_id']})


class PropertyDelete(LoginRequiredMixin, TemplateView):
    template_name = 'pecunia/confirm_delete.html'
    success_url = reverse_lazy('property_list')

    def post(self, request, *args, **kwargs):
        if "confirm" in request.POST:
            m.Property.objects.get(display_id=self.kwargs[
                'display_id']).delete()  # TODO: prendre en compte le fait qu’elle puisse etre utilisée
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = f"Property P{self.kwargs['display_id']}"
        return context
