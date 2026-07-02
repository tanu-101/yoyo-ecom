from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone

from apps.accounts.constants import StaffPermissionCode, UserRole
from apps.accounts.models import Address, User
from apps.accounts.services.staff_permissions import set_staff_permissions
from apps.accounts.services.users import create_user
from apps.carts.models import Cart, CartItem
from apps.catalog.constants import ProductStatus, VariantStatus
from apps.catalog.models import Category, Product, Variant
from apps.coupons.constants import DiscountType
from apps.coupons.models import Coupon
from apps.inventory.constants import InventoryTransactionType
from apps.inventory.models import InventoryTransaction
from apps.notifications.constants import NotificationChannel, NotificationStatus
from apps.notifications.models import Notification, NotificationPreference
from apps.orders.constants import OrderStatus, PaymentStatus
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.payments.constants import PaymentProvider, PaymentState
from apps.payments.models import Payment, PaymentEvent
from apps.reviews.constants import ReviewStatus
from apps.reviews.models import Review
from apps.shipping.constants import TrackingStatus
from apps.shipping.models import OrderTracking, ShippingMethod
from apps.wishlist.models import WishlistItem

PASSWORD = "SeedPass123!"


class Command(BaseCommand):
    help = "Seed development/demo data for all domains."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--customers", type=int, default=5)
        parser.add_argument("--staff", type=int, default=2)
        parser.add_argument("--admins", type=int, default=1)
        parser.add_argument("--superusers", type=int, default=0)
        parser.add_argument("--addresses-per-customer", type=int, default=1)
        parser.add_argument("--categories", type=int, default=5)
        parser.add_argument("--products-per-category", type=int, default=3)
        parser.add_argument("--variants-per-product", type=int, default=2)
        parser.add_argument("--coupons", type=int, default=3)
        parser.add_argument("--shipping-methods", type=int, default=3)
        parser.add_argument("--orders", type=int, default=3)
        parser.add_argument("--reviews", type=int, default=5)
        parser.add_argument("--wishlist-items", type=int, default=3)
        parser.add_argument("--prefix", default="seed")
        parser.add_argument("--password", default=PASSWORD)

    def handle(self, *args: Any, **options: Any) -> None:
        password = options["password"]
        prefix = options["prefix"]

        admin_users = self._seed_users(
            count=options["admins"],
            role=UserRole.ADMIN,
            prefix=prefix,
            kind="admin",
            password=password,
        )
        superusers = self._seed_users(
            count=options["superusers"],
            role=UserRole.ADMIN,
            prefix=prefix,
            kind="superuser",
            password=password,
            is_superuser=True,
        )
        actor = superusers[0] if superusers else admin_users[0] if admin_users else None

        customers = self._seed_users(
            count=options["customers"],
            role=UserRole.CUSTOMER,
            prefix=prefix,
            kind="customer",
            password=password,
        )
        self._seed_addresses(customers=customers, per_customer=options["addresses_per_customer"])

        self._seed_staff(
            count=options["staff"],
            prefix=prefix,
            password=password,
            granted_by=actor,
        )

        self._seed_notification_preferences(customers)
        categories = self._seed_categories(options["categories"], prefix)
        products = self._seed_products(categories, options["products_per_category"], prefix)
        variants = self._seed_variants(products, options["variants_per_product"], prefix)
        self._seed_inventory(variants, actor)
        self._seed_coupons(options["coupons"], prefix)
        self._seed_shipping_methods(options["shipping_methods"], prefix)

        self._seed_carts(customers, products, variants)
        self._seed_wishlist_items(customers, products, options["wishlist_items"])

        orders = self._seed_orders(customers, variants, options["orders"], prefix)
        self._seed_payments(orders)

        self._seed_reviews(customers, products, orders, options["reviews"])
        self._seed_notifications(customers)

        self.stdout.write(self.style.SUCCESS("Seed data ready."))

    def _seed_users(
        self,
        *,
        count: int,
        role: str,
        prefix: str,
        kind: str,
        password: str,
        is_superuser: bool = False,
    ) -> list[User]:
        users: list[User] = []
        for index in range(1, count + 1):
            email = f"{prefix}-{kind}-{index}@example.com"
            user = User.objects.filter(email=email).first()
            if user is None:
                user = create_user(
                    email=email,
                    password=password,
                    role=role,
                    first_name=kind.title(),
                    last_name=str(index),
                    phone=f"+880100000{index:04d}",
                    is_active=True,
                )
                if is_superuser:
                    user.is_staff = True
                    user.is_superuser = True
                    user.save(update_fields=["is_staff", "is_superuser"])
            users.append(user)
        return users

    def _seed_staff(
        self,
        *,
        count: int,
        prefix: str,
        password: str,
        granted_by: User | None,
    ) -> None:
        staff_users = self._seed_users(
            count=count,
            role=UserRole.STAFF,
            prefix=prefix,
            kind="staff",
            password=password,
        )
        if granted_by is not None:
            for user in staff_users:
                set_staff_permissions(
                    staff_user=user,
                    permission_updates=[
                        {"code": StaffPermissionCode.ORDERS_VIEW, "is_enabled": True},
                        {"code": StaffPermissionCode.PRODUCTS_VIEW, "is_enabled": True},
                    ],
                    granted_by=granted_by,
                )

    def _seed_addresses(self, *, customers: list[User], per_customer: int) -> None:
        for user in customers:
            for index in range(1, per_customer + 1):
                line1 = f"Seed House {index}"
                if Address.objects.filter(user=user, line1=line1, deleted_at__isnull=True).exists():
                    continue
                Address.objects.create(
                    user=user,
                    full_name=f"{user.first_name} {user.last_name}".strip() or user.email,
                    phone=user.phone or "+8801000000000",
                    line1=line1,
                    city="Dhaka",
                    state="Dhaka",
                    postal_code="1207",
                    country="BD",
                    is_default=index == 1,
                )

    def _seed_notification_preferences(self, customers: list[User]) -> None:
        for user in customers:
            NotificationPreference.objects.get_or_create(user=user)

    def _seed_categories(self, count: int, prefix: str) -> list[Category]:
        categories: list[Category] = []
        for index in range(1, count + 1):
            name = f"{prefix.title()} Category {index}"
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={"slug": f"{prefix}-category-{index}", "is_active": True},
            )
            categories.append(cat)
        return categories

    def _seed_products(
        self,
        categories: list[Category],
        per_category: int,
        prefix: str,
    ) -> list[Product]:
        products: list[Product] = []
        pidx = 1
        for cat in categories:
            for _ in range(per_category):
                name = f"{prefix.title()} Product {pidx}"
                prod, _ = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        "category": cat,
                        "slug": f"{prefix}-product-{pidx}",
                        "description": f"Description for {name}.",
                        "base_price": "49.99",
                        "status": ProductStatus.ACTIVE,
                    },
                )
                products.append(prod)
                pidx += 1
        return products

    def _seed_variants(
        self,
        products: list[Product],
        per_product: int,
        prefix: str,
    ) -> list[Variant]:
        variants: list[Variant] = []
        vidx = 1
        for prod in products:
            for v in range(1, per_product + 1):
                sku = f"{prefix.upper()}-{vidx:05d}"
                vtype = "Standard" if v == 1 else "Premium"
                var, _ = Variant.objects.get_or_create(
                    sku=sku,
                    defaults={
                        "product": prod,
                        "name": f"{vtype} - {prod.name}",
                        "price": "59.99" if v == 1 else "79.99",
                        "stock_quantity": 25 + v * 10,
                        "status": VariantStatus.ACTIVE,
                        "image": "",
                    },
                )
                variants.append(var)
                vidx += 1
        return variants

    def _seed_inventory(self, variants: list[Variant], created_by: User | None) -> None:
        for var in variants:
            if not InventoryTransaction.objects.filter(variant=var).exists():
                InventoryTransaction.objects.create(
                    variant=var,
                    transaction_type=InventoryTransactionType.MANUAL_ADJUSTMENT,
                    quantity_changed=var.stock_quantity,
                    stock_before=0,
                    stock_after=var.stock_quantity,
                    notes="Initial stock via seed.",
                    created_by=created_by,
                )

    def _seed_coupons(self, count: int, prefix: str) -> None:
        for index in range(1, count + 1):
            code = f"{prefix.upper()}{index:04d}"
            Coupon.objects.get_or_create(
                code=code,
                defaults={
                    "discount_type": DiscountType.PERCENTAGE,
                    "discount_value": 10.0 * index,
                    "min_order_value": 50.0,
                    "per_customer_limit": 1,
                    "valid_from": timezone.now(),
                    "valid_until": timezone.now() + timedelta(days=30),
                    "is_active": True,
                },
            )

    def _seed_shipping_methods(self, count: int, prefix: str) -> None:
        names = ["Standard", "Express", "Overnight"]
        prices = [5.00, 15.00, 30.00]
        per_kg = [1.00, 3.00, 5.00]
        for index in range(count):
            name = names[index] if index < len(names) else f"{prefix.title} Method {index}"
            ShippingMethod.objects.get_or_create(
                code=f"{prefix}-ship-{index}",
                defaults={
                    "name": name,
                    "base_price": prices[index] if index < len(prices) else 10.00,
                    "price_per_kg": per_kg[index] if index < len(per_kg) else 2.00,
                    "is_active": True,
                },
            )

    def _seed_carts(
        self,
        customers: list[User],
        products: list[Product],
        variants: list[Variant],
    ) -> None:
        for user in customers[:3]:
            cart, _ = Cart.objects.get_or_create(customer=user)
            if not cart.items.exists():
                for i in range(2):
                    v = variants[(customers.index(user) * 2 + i) % len(variants)]
                    CartItem.objects.create(
                        cart=cart,
                        product=v.product,
                        variant=v,
                        quantity=1 + i,
                        unit_price=v.price,
                    )

    def _seed_wishlist_items(
        self,
        customers: list[User],
        products: list[Product],
        count: int,
    ) -> None:
        for user in customers[:3]:
            for i in range(count):
                prod = products[(customers.index(user) * count + i) % len(products)]
                WishlistItem.objects.get_or_create(customer=user, product=prod)

    def _seed_orders(
        self,
        customers: list[User],
        variants: list[Variant],
        count: int,
        prefix: str,
    ) -> list[Order]:
        orders: list[Order] = []
        for index in range(1, count + 1):
            customer = customers[(index - 1) % len(customers)]
            order_num = f"ORD-2026-S{index:06d}"
            order, created = Order.objects.get_or_create(
                order_number=order_num,
                defaults={
                    "customer": customer,
                    "status": OrderStatus.PLACED if index < count else OrderStatus.DELIVERED,
                    "payment_status": PaymentStatus.PAID,
                    "subtotal": 99.99,
                    "discount_amount": 0.00,
                    "shipping_cost": 10.00,
                    "tax_amount": 5.00,
                    "total_amount": 114.99,
                },
            )
            if created:
                v = variants[(index - 1) % len(variants)]
                OrderItem.objects.create(
                    order=order,
                    product=v.product,
                    variant=v,
                    product_name=v.product.name,
                    variant_name=v.name,
                    sku=v.sku,
                    quantity=1,
                    unit_price="99.99",
                    line_total="99.99",
                )
                OrderStatusHistory.objects.create(
                    order=order,
                    from_status=None,
                    to_status=order.status,
                    reason="Seed order.",
                )
            orders.append(order)
        return orders

    def _seed_payments(self, orders: list[Order]) -> None:
        for order in orders:
            if not Payment.objects.filter(order=order).exists():
                payment = Payment.objects.create(
                    order=order,
                    provider=PaymentProvider.STRIPE,
                    provider_payment_intent_id=f"pi_seed_{order.order_number.lower()}",
                    amount=float(order.total_amount),
                    currency="USD",
                    status=PaymentState.SUCCEEDED,
                )
                PaymentEvent.objects.create(
                    provider=PaymentProvider.STRIPE,
                    event_id=f"evt_seed_{order.order_number.lower()}",
                    event_type="payment_intent.succeeded",
                    payload={"data": {"object": {"id": payment.provider_payment_intent_id}}},
                )
                if order.status == OrderStatus.DELIVERED:
                    OrderTracking.objects.get_or_create(
                        order=order,
                        defaults={
                            "carrier": "FedEx",
                            "tracking_number": f"TRK_SEED_{order.order_number}",
                            "status": TrackingStatus.DELIVERED,
                        },
                    )

    def _seed_reviews(
        self,
        customers: list[User],
        products: list[Product],
        orders: list[Order],
        count: int,
    ) -> None:
        for i in range(count):
            customer = customers[i % len(customers)]
            product = products[i % len(products)]
            order_item = OrderItem.objects.filter(
                order__customer=customer,
                product=product,
            ).first()
            if order_item is None:
                continue
            Review.objects.get_or_create(
                product=product,
                customer=customer,
                order_item=order_item,
                defaults={
                    "rating": 4 + (i % 2),
                    "title": "Great product",
                    "content": f"Review {i + 1}: Really liked this product.",
                    "status": ReviewStatus.APPROVED if i % 2 == 0 else ReviewStatus.PENDING,
                },
            )

    def _seed_notifications(self, customers: list[User]) -> None:
        for user in customers[:3]:
            Notification.objects.get_or_create(
                user=user,
                channel=NotificationChannel.IN_APP,
                notification_type="welcome",
                defaults={
                    "subject": "Welcome!",
                    "body": "Welcome to the store!",
                    "status": NotificationStatus.SENT,
                },
            )
