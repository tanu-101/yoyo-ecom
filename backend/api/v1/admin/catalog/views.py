from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.catalog.models import (
    Category,
    Product,
    ProductImage,
    Variant,
    VariantAttribute,
    VariantAttributeValue,
)
from apps.common.permissions import IsAdminOrStaffWithPermission

from .serializers import (
    AdminCategorySerializer,
    AdminProductImageSerializer,
    AdminProductSerializer,
    AdminVariantAttributeSerializer,
    AdminVariantAttributeValueSerializer,
    AdminVariantSerializer,
)


class AdminCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = AdminCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrStaffWithPermission]
    required_staff_permission = "products.view"


class AdminProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = AdminProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrStaffWithPermission]
    required_staff_permission = "products.view"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AdminProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = AdminProductImageSerializer
    permission_classes = [IsAuthenticated, IsAdminOrStaffWithPermission]
    required_staff_permission = "products.view"


class AdminVariantAttributeViewSet(viewsets.ModelViewSet):
    queryset = VariantAttribute.objects.all()
    serializer_class = AdminVariantAttributeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrStaffWithPermission]
    required_staff_permission = "products.view"


class AdminVariantAttributeValueViewSet(viewsets.ModelViewSet):
    queryset = VariantAttributeValue.objects.all()
    serializer_class = AdminVariantAttributeValueSerializer
    permission_classes = [IsAuthenticated, IsAdminOrStaffWithPermission]
    required_staff_permission = "products.view"


class AdminVariantViewSet(viewsets.ModelViewSet):
    queryset = Variant.objects.all()
    serializer_class = AdminVariantSerializer
    permission_classes = [IsAuthenticated, IsAdminOrStaffWithPermission]
    required_staff_permission = "products.view"
