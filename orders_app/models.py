from django.db import models
from django.utils import timezone
from auth_app.models import User

class Order(models.Model):
    class OfferTypes(models.TextChoices):
        BASIC = "basic", "basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    class Roles(models.TextChoices):
        BASIC = "basic", "basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    customer_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer_orders'
    )
    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='business_orders'
    )
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=20,
        choices=OfferTypes.choices,
        default=OfferTypes.BASIC,
    
    )