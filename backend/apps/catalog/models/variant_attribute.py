from __future__ import annotations

from django.db import models

from apps.common.models.base import TimeStampedModel


class VariantAttribute(TimeStampedModel):
    name: models.CharField = models.CharField(max_length=100, unique=True)
    slug: models.SlugField = models.SlugField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.name
