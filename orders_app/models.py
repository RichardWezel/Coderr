from django.db import models
from django.utils import timezone
from auth_app.models import CustomUser 
from offers_app.models import OfferDetail, Offer


class Order(Offer):

    class OrderStatus(models.TextChoices):
        IN_PROGRESS = "'in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    offer_detail_id = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name="order")
    customer_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='customer_orders'
    )
    business_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='business_orders'
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.IN_PROGRESS,
    )