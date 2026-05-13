from __future__ import annotations

from rest_framework import serializers

from apps.accounts.constants import UserRole


class AdminUserSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    role = serializers.ChoiceField(choices=UserRole.choices)
    phone = serializers.CharField(allow_blank=True)
    profile_picture = serializers.CharField(allow_blank=True)
    is_active = serializers.BooleanField()
    is_email_verified = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    permissions = serializers.ListField(child=serializers.CharField())


class AdminUserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserRole.choices, default=UserRole.CUSTOMER)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False, default=True)


class AdminUserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    is_email_verified = serializers.BooleanField(required=False)


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)


class SetRoleSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=UserRole.choices)
