from django.db import models
from auth_app.models import CustomUser


class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='profile')
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True) 
    last_name = models.CharField(max_length=30, blank=True)
    file = models.FileField(upload_to='profile_files/', blank=True)
    location = models.CharField(max_length=100, blank=True)
    tel = models.CharField(max_length=15, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=50, blank=True)
    type = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ['created_at']
    def __str__(self):
        return self.username
    
