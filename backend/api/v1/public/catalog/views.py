from __future__ import annotations

from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.catalog.selectors.products import get_active_products, get_categories

from .serializers import CategorySerializer, ProductDetailSerializer, ProductListSerializer


class CategoryListView(generics.ListAPIView):
    queryset = get_categories()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class ProductListView(generics.ListAPIView):
    queryset = get_active_products()
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filterset_fields = ["category", "is_featured"]
    search_fields = ["name", "description"]


class ProductDetailView(generics.RetrieveAPIView):
    queryset = get_active_products()
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"
