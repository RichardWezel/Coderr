from django.db import models
from auth_app.models import CustomUser

# Create your models here.

class Offer(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    image = models.FileField(upload_to='offer_images/', blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    min_delivery_time = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class OfferDetail(models.Model):
    class Roles(models.TextChoices):
        BASIC = "basic", "basic"
        STANDARD = "standard", "Standard"
        PREMIUM = "premium", "Premium"

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="details", null=True, blank=True)  # 👈 Verbindung
     
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(default=0)
    delivery_time_in_days = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    features = models.JSONField(default=list, help_text="List of feature strings")
    offer_type = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.BASIC,
    )

    class Meta:
        verbose_name = "Offer Detail"
        verbose_name_plural = "Offer Details"
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['offer', 'offer_type'], name='uniq_offer_offer_type')
        ]

    def __str__(self):
        return f"{self.title} - {self.offer_type}"

