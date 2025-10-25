from django.views.generic import TemplateView

from .api import PropertyApiView, SearchPropertyApiView, ItemApiView, NewItemApiView, SearchItemApiView, \
    StatementAddApiView, StatementUpdateApiView, StatementApiView, StatementDeleteApiView, QualifierAddApiView, \
    QualifierDeleteApiView
from .document import DocumentDashboard, DocumentDisplay, DocumentCreation, DocumentUpdateMetadata, \
    DocumentDelete, DocumentUpdateText, AnnotatorApiView
from .person import PersonDashboard, PersonDisplay, PersonCreation, PersonUpdate, PersonDelete
from .place import PlaceDashboard, PlaceDisplay, PlaceCreation, PlaceUpdate, PlaceDelete
from .wikibase import InstanceDashboardView, ItemDashboard, ItemCreation, ItemDisplay, ItemUpdateLabelDescription, \
    ItemDelete, PropertyDashboard, PropertyCreation, PropertyDisplay, PropertyUpdateLabelDescription, PropertyDelete


class Home(TemplateView):
    template_name = 'pecunia/index.html'

