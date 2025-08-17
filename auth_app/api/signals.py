from django.db.models.signals import post_save
from django.dispatch import receiver
from auth_app.models import CustomUser
from profile_app.models import UserProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance: CustomUser, created, **kwargs):
    if created:
        # Profil mit Default-Werten aus dem User anlegen
        UserProfile.objects.create(
            user=instance,
            username=instance.username,   # spiegelt den Usernamen
            email=instance.email or "",   # falls leer
            type=instance.type,           # spiegelt die User-Rolle
        )