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

import pecunia.views as views
from .rest import router

urlpatterns = [

    path("", views.Home.as_view(), name="index"),
    path('', include('pecunia.urls.domain')),
    path('', include('pecunia.urls.wikibase')),

    path("api/annotator", views.AnnotatorApiView.as_view(), name="api_annotator"),

    path('api/', include(router.urls)),
    path("api/property/search/<str:search>", views.SearchPropertyApiView.as_view(), name="api_search_property"),
    path("api/items/search/<str:search>", views.SearchItemApiView.as_view(), name="api_search_item"),
    path("api/statement/add", views.StatementAddApiView.as_view(), name="api_statement_snak_new"),
    path("api/statement/update", views.StatementUpdateApiView.as_view(), name="api_statement_snak_update"),
    path("api/statement/<int:statement_id>", views.StatementApiView.as_view(), name="api_statements"),
    path("api/statement/delete", views.StatementDeleteApiView.as_view(), name="api_statement_delete"),
    path("api/qualifier/add", views.QualifierAddApiView.as_view(), name="api_new_qualifier"),
    path("api/qualifier/delete", views.QualifierDeleteApiView.as_view(), name="api_qualifier_delete"),
]
