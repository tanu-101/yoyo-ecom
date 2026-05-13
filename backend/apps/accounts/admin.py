from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Address, StaffPermission, User, UserOTP


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "role", "is_active", "is_staff", "date_joined")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        *(DjangoUserAdmin.fieldsets or ()),
        (
            "E-Commerce Profile",
            {"fields": ("role", "phone", "is_email_verified", "deleted_at")},
        ),
    )
    add_fieldsets = (
        *(DjangoUserAdmin.add_fieldsets or ()),
        (
            "E-Commerce Profile",
            {"fields": ("email", "role")},
        ),
    )


@admin.register(StaffPermission)
class StaffPermissionAdmin(admin.ModelAdmin):
    list_display = ("user", "permission_code", "is_enabled", "granted_by", "granted_at")
    list_filter = ("permission_code", "is_enabled")
    search_fields = ("user__email", "permission_code")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "city", "country", "is_default")
    list_filter = ("country", "is_default")
    search_fields = ("user__email", "full_name", "city")


@admin.register(UserOTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "expires_at", "consumed_at")
    list_filter = ("purpose", "consumed_at")
    search_fields = ("user__email",)
    readonly_fields = ("code_hash",)
