from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        BUSINESS = "business", "Business"

    type = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.CUSTOMER,
    )

    def __str__(self):
        return f"{self.username} ({self.type})"
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["username"]  