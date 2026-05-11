from django.db import models


class TrackingStatus(models.TextChoices):
    PROCESSING = "processing", "Processing"
    IN_TRANSIT = "in_transit", "In transit"
    OUT_FOR_DELIVERY = "out_for_delivery", "Out for delivery"
    DELIVERED = "delivered", "Delivered"
    EXCEPTION = "exception", "Exception"
