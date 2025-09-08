from django.db.models.signals import post_save
from django.dispatch import receiver
from auth_app.models import CustomUser
from profile_app.models import UserProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance: CustomUser, created, **kwargs):
    """Signal to create a UserProfile whenever a new CustomUser is created."""
    if created:
        UserProfile.objects.create(
            user=instance,
            username=instance.username,   
            email=instance.email or "",   
            type=instance.type,           
        )