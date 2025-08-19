from django.db import models

from auth_app.models import CustomUser

class Review(models.Model):
    business_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['id']

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.business_user.username} - Rating: {self.rating}"