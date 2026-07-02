from __future__ import annotations

from django.urls import path

from . import views

app_name = "customer_returns"

urlpatterns = [
    path("", views.CreateReturnView.as_view(), name="create-return"),
    path("list/", views.CustomerReturnListView.as_view(), name="return-list"),
    path("<uuid:return_id>/", views.CustomerReturnDetailView.as_view(), name="return-detail"),
]
