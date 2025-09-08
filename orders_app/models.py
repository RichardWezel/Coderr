from django.db import models
from django.utils import timezone
from auth_app.models import CustomUser 
from offers_app.models import OfferDetail, Offer


class Order(models.Model):
    """Represents a placed order between a customer and business user."""

    class OrderStatus(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

   # Referenzen
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="orders")
    offer_detail = models.ForeignKey(OfferDetail, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)

    # Beteiligte Nutzer
    customer_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='customer_orders')
    business_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='business_orders')
    
    # Snapshot-Felder (zum Zeitpunkt der Bestellung)
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=20)

    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.IN_PROGRESS)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.pk} - {self.title} ({self.status})"
