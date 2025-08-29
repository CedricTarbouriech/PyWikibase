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

from wikibase import views
from .rest import router

urlpatterns = [
    path('api/', include(router.urls)),
    path("api/properties", views.PropertyApiView.as_view(), name="api_properties"),
    path("api/property/<int:prop_id>", views.PropertyApiView.as_view(), name="api_properties"),
    path("api/items", views.ItemApiView.as_view(), name="api_items"),
    path("api/items/new", views.NewItemApiView.as_view(), name="api_new_item"),
    path("api/items/search/<str:search>", views.SearchItemApiView.as_view(), name="api_search_item"),
    path("api/statement/add", views.StatementAddApiView.as_view(), name="api_statement_snak_new"),
    path("api/statement/update", views.StatementUpdateApiView.as_view(), name="api_statement_snak_update"),
    path("api/statement/<int:statement_id>", views.StatementApiView.as_view(), name="api_statements"),
    path("api/statement/delete", views.StatementDeleteApiView.as_view(), name="api_statement_delete"),
    path("api/qualifier/add", views.QualifierAddApiView.as_view(), name="api_new_qualifier"),
    path("api/qualifier/delete", views.QualifierDeleteApiView.as_view(), name="api_qualifier_delete"),
    path("item/", views.ItemDashboard.as_view(), name="item_list"),
    path("item/new/", views.ItemCreation.as_view(), name="item_create"),
    path("item/<int:display_id>/", views.ItemDisplay.as_view(), name="item_display"),
    path("item/updatelabeldescription/<int:display_id>/<str:lang>/",
         views.ItemUpdateLabelDescription.as_view(), name="item_updatelabeldescription"),
    path("item/delete/<int:display_id>/", views.ItemDelete.as_view(), name="item_delete"),
    path("property/", views.PropertyDashboard.as_view(), name="property_list"),
    path("property/new/", views.PropertyCreation.as_view(), name="property_create"),
    path("property/<int:display_id>/", views.PropertyDisplay.as_view(), name="property_display"),
    path("property/update/labeldescription/<int:display_id>/<str:lang>/",
         views.PropertyUpdateLabelDescription.as_view(), name="property_update_labeldescription"),
    path("property/delete/<int:display_id>/", views.PropertyDelete.as_view(), name="property_delete"),
]
