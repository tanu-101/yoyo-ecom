from __future__ import annotations

from django.urls import path

from . import views

app_name = "public_shipping"

urlpatterns = [
    path("methods/", views.ShippingMethodListView.as_view(), name="shipping-methods"),
]
