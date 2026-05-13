from __future__ import annotations

from django.urls import path

from .views import (
    AdminResetPasswordView,
    AdminSetRoleView,
    AdminUserActionView,
    AdminUserDetailView,
    AdminUserListCreateView,
)

app_name = "admin_users"

urlpatterns = [
    path("", AdminUserListCreateView.as_view(), name="user-list"),
    path("<uuid:user_id>/", AdminUserDetailView.as_view(), name="user-detail"),
    path(
        "<uuid:user_id>/activate/",
        AdminUserActionView.as_view(action="activate"),
        name="user-activate",
    ),
    path(
        "<uuid:user_id>/deactivate/",
        AdminUserActionView.as_view(action="deactivate"),
        name="user-deactivate",
    ),
    path(
        "<uuid:user_id>/soft-delete/",
        AdminUserActionView.as_view(action="soft_delete"),
        name="user-soft-delete",
    ),
    path("<uuid:user_id>/reset-password/", AdminResetPasswordView.as_view(), name="reset-password"),
    path("<uuid:user_id>/set-role/", AdminSetRoleView.as_view(), name="set-role"),
]
