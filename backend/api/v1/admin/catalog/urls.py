from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminCategoryViewSet,
    AdminProductImageViewSet,
    AdminProductViewSet,
    AdminVariantAttributeValueViewSet,
    AdminVariantAttributeViewSet,
    AdminVariantViewSet,
)

router = DefaultRouter()
router.register("categories", AdminCategoryViewSet, basename="admin-category")
router.register("products", AdminProductViewSet, basename="admin-product")
router.register("product-images", AdminProductImageViewSet, basename="admin-product-image")
router.register("attributes", AdminVariantAttributeViewSet, basename="admin-attribute")
router.register(
    "attribute-values", AdminVariantAttributeValueViewSet, basename="admin-attribute-value"
)
router.register("variants", AdminVariantViewSet, basename="admin-variant")

urlpatterns = [
    path("", include(router.urls)),
]
