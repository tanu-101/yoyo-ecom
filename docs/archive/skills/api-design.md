# API Design Patterns

## REST API Structure

### URL Patterns

```
/api/v1/public/          # Public endpoints (no auth required)
/api/v1/customer/        # Customer authenticated endpoints
/api/v1/admin/           # Admin/staff endpoints
/api/v1/webhooks/        # Webhook endpoints (Stripe, etc.)
```

### HTTP Methods

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products/` | List products |
| GET | `/products/{id}/` | Get product detail |
| POST | `/products/` | Create product |
| PUT | `/products/{id}/` | Update product (full) |
| PATCH | `/products/{id}/` | Partial update |
| DELETE | `/products/{id}/` | Soft delete product |

## Serializer Patterns

### ModelSerializer

```python
from __future__ import annotations

from rest_framework import serializers

from apps.products.models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price',
            'compare_at_price', 'category', 'category_id',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
```

### Nested Serializers

```python
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'total_amount',
            'shipping_address', 'items', 'user_email',
            'created_at', 'updated_at'
        ]
```

### Write-Only Nested

```python
class CartItemCreateSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
```

### Serializer Methods

```python
class ProductSerializer(serializers.ModelSerializer):
    discount_percentage = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'discount_percentage', 'is_in_stock']

    def get_discount_percentage(self, obj):
        if obj.compare_at_price and obj.compare_at_price > obj.price:
            return ((obj.compare_at_price - obj.price) / obj.compare_at_price) * 100
        return 0

    def get_is_in_stock(self, obj):
        return obj.inventory_quantity > 0
```

## ViewSet Patterns

### Standard ModelViewSet

```python
from __future__ import annotations

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.products.selectors.product_selector import ProductSelector
from apps.products.services.product_service import ProductService
from apps.products.serializers.product_serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filterset_class = ProductFilter

    def get_queryset(self):
        return ProductSelector.get_active_products()

    def perform_create(self, serializer):
        ProductService.create_product(serializer.validated_data)

    def perform_update(self, serializer):
        ProductService.update_product(
            serializer.instance,
            serializer.validated_data
        )
```

### Custom Actions

```python
@action(detail=True, methods=['post'])
def activate(self, request, pk=None):
    product = ProductSelector.get_by_id(pk)
    if not product:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    ProductService.activate(product)
    return Response({'status': 'activated'})

@action(detail=False, methods=['get'])
def featured(self, request):
    products = ProductSelector.get_featured()
    serializer = self.get_serializer(products, many=True)
    return Response(serializer.data)
```

### Permission Classes

```python
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Default

    @action(detail=False, methods=['get'])
    def public_action(self, request):
        # Override for public access
        return Response({'data': 'public'})

class AdminProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]  # Admin only
```

## Filtering

### Django Filter Setup

```python
# apps/products/filters.py
from __future__ import annotations

import django_filters

from apps.products.models import Product

class ProductFilter(django_filters.FilterSet):
    category = django_filters.UUIDFilter(field_name='category__id')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    is_active = django_filters.BooleanFilter(field_name='is_active')
    search = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'is_active', 'search']
```

### Ordering

```python
from rest_framework.filters import OrderingFilter

class ProductViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['price', 'name', 'created_at']
    ordering = ['-created_at']
```

## Pagination

Use custom pagination from `apps/common/pagination.py`:

```python
from apps.common.pagination import DefaultPageNumberPagination

class ProductViewSet(viewsets.ModelViewSet):
    pagination_class = DefaultPageNumberPagination
    page_size = 20
```

## Response Patterns

### Success Response

```python
from rest_framework import status
from rest_framework.response import Response

# Created
return Response(serializer.data, status=status.HTTP_201_CREATED)

# Updated
return Response(serializer.data, status=status.HTTP_200_OK)

# No content
return Response(status=status.HTTP_204_NO_CONTENT)
```

### Error Response

```python
# Validation error
return Response(
    {'errors': serializer.errors},
    status=status.HTTP_400_BAD_REQUEST
)

# Not found
return Response(
    {'error': 'Product not found'},
    status=status.HTTP_404_NOT_FOUND
)

# Permission denied
return Response(
    {'error': 'You do not have permission'},
    status=status.HTTP_403_FORBIDDEN
)
```

## URL Configuration

### App URLs

```python
# apps/products/urls.py
from __future__ import annotations

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.products.views.product_views import ProductViewSet

router = DefaultRouter()
router.register(r'', ProductViewSet, basename='products')

urlpatterns = [
    path('', include(router.urls)),
]
```

### Root URLs

```python
# config/urls.py
from __future__ import annotations

from django.urls import path, include

urlpatterns = [
    # Public endpoints
    path('api/v1/public/', include([
        path('', include('apps.catalog.urls')),
        path('', include('apps.reviews.urls')),
    ])),

    # Customer endpoints
    path('api/v1/customer/', include([
        path('', include('apps.carts.urls')),
        path('', include('apps.orders.urls')),
        path('', include('apps.wishlist.urls')),
    ])),

    # Admin endpoints
    path('api/v1/admin/', include([
        path('', include('apps.inventory.urls')),
        path('', include('apps.coupons.urls')),
        path('', include('apps.analytics.urls')),
    ])),

    # Webhooks
    path('api/v1/webhooks/', include([
        path('stripe/', include('apps.payments.webhook_urls')),
    ])),
]
```

## OpenAPI Schema

Use drf-spectacular for auto-generated API docs:

```python
from drf_spectacular.utils import extend_schema, extend_view

class ProductViewSet(viewsets.ModelViewSet):
    @extend_schema(
        summary="List products",
        description="Returns a paginated list of all active products",
        responses={200: ProductSerializer(many=True)},
        tags=['Products']
    )
    def list(self, request, *args, **kwargs):
        pass
```

## Authentication

### JWT Setup

```python
# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Public Endpoints

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def public_products(request):
    # Public endpoint - no auth required
    pass
```

## Best Practices

1. **Use nouns for resources** - `/products`, `/orders`, not `/getProducts`
2. **Use HTTP verbs** - GET, POST, PUT, PATCH, DELETE
3. **Use plural nouns** - `/products` not `/product`
4. **Nest resources logically** - `/orders/{id}/items`
5. **Version your API** - `/api/v1/`, `/api/v2/`
6. **Return appropriate status codes** - 200, 201, 204, 400, 404, etc.
7. **Use consistent error format** - `{'error': 'message', 'errors': {}}`
8. **Paginate large lists** - Use cursor or page-based pagination
9. **Use UUIDs in URLs** - Not integer IDs
10. **Document your API** - Use drf-spectacular for OpenAPI