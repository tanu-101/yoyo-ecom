from django.db import models


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    STAFF = "staff", "Staff"
    CUSTOMER = "customer", "Customer"


class StaffPermissionCode(models.TextChoices):
    PRODUCTS_VIEW = "products.view", "View products"
    PRODUCTS_CREATE = "products.create", "Create products"
    PRODUCTS_UPDATE = "products.update", "Update products"
    ORDERS_VIEW = "orders.view", "View orders"
    ORDERS_UPDATE_STATUS = "orders.update_status", "Update order status"
    RETURNS_VIEW = "returns.view", "View returns"
    SUPPORT_VIEW_CUSTOMERS = "support.view_customers", "View customers"
    INVENTORY_VIEW = "inventory.view", "View inventory"

