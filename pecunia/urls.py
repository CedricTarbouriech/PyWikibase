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
from django.urls import path, include

from pecunia import views

urlpatterns = [
    path("", views.Home.as_view(), name="index"),
    path("document/", views.DocumentDashboard.as_view(), name="document_list"),
    path("document/new/", views.DocumentCreation.as_view(), name="document_create"),
    path("document/<int:display_id>/", views.DocumentDisplay.as_view(), name="document_display"),
    path("document/update/<int:display_id>/", views.DocumentUpdate.as_view(), name="document_update"),
    path("document/delete/<int:display_id>/", views.DocumentDelete.as_view(), name="document_delete"),
    path("person/", views.PersonDashboard.as_view(), name="person_list"),
    path("person/new/", views.PersonCreation.as_view(), name="person_create"),
    path("person/<int:display_id>/", views.PersonDisplay.as_view(), name="person_display"),
    path("person/update/<int:display_id>/", views.PersonUpdate.as_view(), name="person_update"),
    path("person/delete/<int:display_id>/", views.PersonDelete.as_view(), name="person_delete"),
    path("place/", views.PlaceDashboard.as_view(), name="place_list"),
    path("place/new/", views.PlaceCreation.as_view(), name="place_create"),
    path("place/<int:pk>/", views.PlaceDisplay.as_view(), name="place_display"),
    path("place/update/<int:display_id>/", views.PlaceUpdate.as_view(), name="place_update"),
    path("place/delete/<int:display_id>/", views.PlaceDelete.as_view(), name="place_delete"),
]
