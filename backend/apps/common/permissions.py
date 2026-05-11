from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.role == "admin")


class IsCustomer(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.role == "customer")


class IsAdminOrStaffWithPermission(BasePermission):
    required_permission: str | None = None

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role == "admin":
            return True

        required_permission = getattr(view, "required_staff_permission", self.required_permission)
        if user.role != "staff" or not required_permission:
            return False

        return user.staff_permissions.filter(
            permission_code=required_permission,
            is_enabled=True,
        ).exists()


class IsOwner(BasePermission):
    owner_field = "user"

    def has_object_permission(self, request, view, obj) -> bool:
        owner_field = getattr(view, "owner_field", self.owner_field)
        owner = getattr(obj, owner_field, None)
        return bool(owner and owner == request.user)


class IsOwnerOrAdmin(BasePermission):
    owner_field = "user"

    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.role == "admin":
            return True

        owner_field = getattr(view, "owner_field", self.owner_field)
        owner = getattr(obj, owner_field, None)
        return bool(owner and owner == request.user)
