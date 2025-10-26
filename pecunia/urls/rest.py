from rest_framework import routers

from pecunia.views.rest import ItemViewSet, PropertyViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'properties', PropertyViewSet)
