from __future__ import annotations

from django.urls import path

from . import views

app_name = "customer_reviews"

urlpatterns = [
    path("", views.CreateReviewView.as_view(), name="create-review"),
    path("<uuid:review_id>/", views.CustomerReviewDetailView.as_view(), name="review-detail"),
]
