from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone


class UUIDModel(models.Model):
    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(UUIDModel):
    created_at: models.DateTimeField = models.DateTimeField(default=timezone.now, editable=False)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    deleted_at: models.DateTimeField | None = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])
