from __future__ import annotations

from django.urls import path

from . import views

app_name = "admin_reviews"

urlpatterns = [
    path("", views.AdminReviewListView.as_view(), name="review-list"),
    path(
        "<uuid:review_id>/approve/", views.AdminApproveReviewView.as_view(), name="review-approve"
    ),
    path("<uuid:review_id>/reject/", views.AdminRejectReviewView.as_view(), name="review-reject"),
]
