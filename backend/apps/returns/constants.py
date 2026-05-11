from django.db import models


class ReturnStatus(models.TextChoices):
    PENDING_REVIEW = "pending_review", "Pending review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    AWAITING_RETURN = "awaiting_return", "Awaiting return"
    IN_TRANSIT = "in_transit", "In transit"
    RECEIVED = "received", "Received"
    PROCESSED = "processed", "Processed"
    REFUNDED = "refunded", "Refunded"
    REPLACED = "replaced", "Replaced"
    COMPLETED = "completed", "Completed"


class ReturnReason(models.TextChoices):
    DAMAGED = "damaged", "Damaged"
    WRONG_ITEM = "wrong_item", "Wrong item"
    MISSING_ITEM = "missing_item", "Missing item"
    DEFECTIVE = "defective", "Defective"
    OTHER = "other", "Other"


class ReturnResolution(models.TextChoices):
    REFUND = "refund", "Refund"
    REPLACEMENT = "replacement", "Replacement"
    STORE_CREDIT = "store_credit", "Store credit"

