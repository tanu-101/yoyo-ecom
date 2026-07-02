from __future__ import annotations

from django.contrib import admin

from apps.reviews.models import Review, ReviewImage, ReviewVote


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("title", "product", "customer", "rating", "status", "created_at")
    list_filter = ("status", "rating")
    search_fields = ("title", "customer__email", "product__name")
    inlines = [ReviewImageInline]


@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ("review", "customer", "vote", "created_at")
