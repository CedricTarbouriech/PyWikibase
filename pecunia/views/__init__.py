from django.views.generic import TemplateView

from .document_views import DocumentDashboard, DocumentDisplay, DocumentCreation, DocumentUpdate, DocumentDelete
from .person_views import PersonDashboard, PersonDisplay, PersonCreation, PersonUpdate, PersonDelete
from .place_views import PlaceDashboard, PlaceDisplay, PlaceCreation, PlaceUpdate, PlaceDelete


class Home(TemplateView):
    template_name = 'pecunia/index.html'
