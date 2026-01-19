from django.views.generic import TemplateView

from .api import StatementApiView, QualifierApiView
from .document import DocumentDashboard, DocumentDisplay, DocumentCreation, DocumentDelete, DocumentUpdateText, \
    AnnotatorApiView
from .person import PersonDashboard, PersonDisplay
from .place import PlaceDashboard, PlaceDisplay
from .wikibase import InstanceDashboardView, ItemDashboard, ItemCreation, ItemDisplay, ItemUpdateLabelDescription, \
    ItemDelete, PropertyDashboard, PropertyCreation, PropertyDisplay, PropertyUpdateLabelDescription, PropertyDelete, \
    WikibaseCheck


class Home(TemplateView):
    template_name = 'pecunia/index.html'
