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
    path("check/", views.WikibaseCheck.as_view(), name="wikibase_check")
]
