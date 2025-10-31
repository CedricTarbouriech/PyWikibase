"""
URL configuration for PyWikibase project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

import pecunia.views as views

urlpatterns = [
    path("document/", views.DocumentDashboard.as_view(), name="document_list"),
    path("document/new/", views.DocumentCreation.as_view(), name="document_create"),
    path("document/<int:display_id>/", views.DocumentDisplay.as_view(), name="document_display"),
    path("document/update/text/<int:display_id>/", views.DocumentUpdateText.as_view(), name="document_update_text"),
    path("document/delete/<int:display_id>/", views.DocumentDelete.as_view(), name="document_delete"),
    path("person/", views.PersonDashboard.as_view(), name="person_list"),
    path("person/<int:display_id>/", views.PersonDisplay.as_view(), name="person_display"),
    path("place/", views.PlaceDashboard.as_view(), name="place_list"),
    path("place/<int:display_id>/", views.PlaceDisplay.as_view(), name="place_display"),
    #
    # path("process/", views.ProcessDashboard.as_view(), name="process_list"),
    # path("vocabulary/", views.VocabularyDashboard.as_view(), name="vocabulary_list"),
]
