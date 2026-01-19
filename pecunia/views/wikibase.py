from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, TemplateView

import pecunia.models as m
from pecunia.forms import ItemLabelDescriptionForm, PropertyLabelDescriptionForm
from pecunia.models import PropertyMapping, ItemMapping

DEFAULT_PAGINATOR_LIMIT = 25


class ModelDashboardView(TemplateView):
    model = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = self.model.objects.all().order_by('display_id')
        paginator = Paginator(items, self.request.GET.get("limit") or DEFAULT_PAGINATOR_LIMIT)

        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context


class InstanceDashboardView(TemplateView):
    item_mapping_key = None

    def dispatch(self, request, *args, **kwargs):
        if not ItemMapping.has(self.item_mapping_key):
            raise Http404(f"Item mapping '{self.item_mapping_key}' does not exist.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        items = m.Item.objects.all()
        result = []
        is_a_prop = PropertyMapping.get('is_a')
        item_mapping = ItemMapping.get(self.item_mapping_key)
        for item in items:
            if not item.statements.exists():
                continue
            if item.statements.filter(mainsnak__property=is_a_prop,
                                      mainsnak__value=item_mapping).exists():
                result.append(item)

        context['items'] = result
        return context


class ItemDashboard(ModelDashboardView):
    template_name = 'wikibase/item_list.html'
    model = m.Item


class ItemDisplay(TemplateView):
    template_name = 'wikibase/item_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        item = m.Item.objects.get(display_id=self.kwargs['display_id'])
        context['item'] = item

        props = m.Property.objects.filter(using_as_property_snaks__used_in_statement__subject=item).distinct()
        statements = [(prop, item.statements.filter(mainsnak__property=prop)) for prop in props]
        prop_order = ({m.PropertyMapping.get('is_a'): -1} |
                      {pop.prop: pop.ordering
                       for pop in m.PropertyOrderPreference.objects.filter(
                          item__using_as_value_snaks__property=m.PropertyMapping.get('is_a'),
                          item__using_as_value_snaks__used_in_statement__subject=item)}
                      )

        max_value = max(prop_order.values()) + 1
        context['statements'] = sorted(statements, key=lambda x: prop_order.get(x[0], max_value))

        context['linked_items'] = m.Item.objects.filter(
            Q(statements__mainsnak__value=item) |
            Q(statements__qualifiers__snak__value=item) |
            Q(statements__reference_records__snaks__snak__value=item)
        ).distinct()

        return context


class ItemUpdateLabelDescription(LoginRequiredMixin, FormView):
    template_name = 'wikibase/item_update_labeldescription.html'
    form_class = ItemLabelDescriptionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        display_id = self.kwargs['display_id']
        lang = self.kwargs['lang']
        item = m.Item.objects.get(display_id=display_id)
        kwargs['display_id'] = display_id
        kwargs['initial']['language'] = lang
        try:
            label = item.labels.get(language=lang)
            kwargs['initial']['label'] = label.text
        except ObjectDoesNotExist:
            pass
        try:
            description = item.descriptions.get(language=lang)
            kwargs['initial']['description'] = description.text
        except ObjectDoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            item = m.Item.objects.get(display_id=self.kwargs['display_id'])
            language_code = self.kwargs['lang']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            if label:
                item.set_label(language_code, label)
            if description:
                item.set_description(language_code, description)
            self.kwargs['display_id'] = item.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('item_display', kwargs={'display_id': self.kwargs['display_id']})


class ItemCreation(LoginRequiredMixin, FormView):
    template_name = 'wikibase/item_creation.html'
    form_class = ItemLabelDescriptionForm

    def form_valid(self, form):
        if form.is_valid():
            # Creation of the property
            item = m.Item.objects.create()
            self.kwargs['display_id'] = item.display_id

            # Creation of the label and the description
            language_code = form.cleaned_data['language']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            if label:
                item.set_label(language_code, label)
            if description:
                item.set_description(language_code, description)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('item_display', kwargs=self.kwargs)


class ItemDelete(LoginRequiredMixin, TemplateView):
    template_name = 'wikibase/confirm_delete.html'
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
    template_name = 'wikibase/property_list.html'
    model = m.Property


class PropertyDisplay(DetailView):
    template_name = 'wikibase/property_detail.html'

    def get_object(self, queryset=None):
        return m.Property.objects.get(display_id=self.kwargs['display_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            prop = kwargs['object']
            stmts = m.Statement.objects.filter(mainsnak__property=prop)
            linked_items = []
            for stmt in stmts:
                linked_items.append(stmt.subject.display_id)
            context['linked_items'] = sorted(linked_items)
        except ObjectDoesNotExist as e:
            raise Http404 from e

        return context


class PropertyCreation(LoginRequiredMixin, FormView):
    template_name = 'wikibase/property_creation.html'
    form_class = PropertyLabelDescriptionForm

    def form_valid(self, form):
        if form.is_valid():
            # Creation of the property
            datatype = form.cleaned_data['type']
            prop = m.Property(data_type=m.Datatype.objects.get(class_name=datatype))
            prop.save()
            self.kwargs['display_id'] = prop.display_id

            # Creation of the label and the description
            language_code = form.cleaned_data['language']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            if label:
                prop.set_label(language_code, label)
            if description:
                prop.set_description(language_code, description)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('property_display', kwargs=self.kwargs)


class PropertyUpdateLabelDescription(LoginRequiredMixin, FormView):
    template_name = 'wikibase/property_update_labeldescription.html'
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
            label = prop.labels.get(language=lang)
            kwargs['initial']['label'] = label.text
        except ObjectDoesNotExist:
            pass
        try:
            description = prop.descriptions.get(language=lang)
            kwargs['initial']['description'] = description.text
        except ObjectDoesNotExist:
            pass
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            prop = m.Property.objects.get(display_id=self.kwargs['display_id'])
            language_code = self.kwargs['lang']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            if label:
                prop.set_label(language_code, label)
            if description:
                prop.set_description(language_code, description)
            self.kwargs['display_id'] = prop.display_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('property_display', kwargs={'display_id': self.kwargs['display_id']})


class PropertyDelete(LoginRequiredMixin, TemplateView):
    template_name = 'wikibase/confirm_delete.html'
    success_url = reverse_lazy('property_list')

    def post(self, request, *args, **kwargs):
        if "confirm" in request.POST:
            m.Property.objects.get(display_id=self.kwargs['display_id']).delete()
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity'] = f"Property P{self.kwargs['display_id']}"
        return context

class WikibaseCheck(LoginRequiredMixin, TemplateView):
    template_name = 'wikibase/check_panel.html'