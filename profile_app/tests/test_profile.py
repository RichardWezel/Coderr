from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from auth_app.models import CustomUser
from profile_app.models import UserProfile
from django.urls import reverse
from rest_framework import status


class CreateProfileOnUserSignalTest(APITestCase):

    def test_profile_is_created_on_user_creation(self):
     
        user = CustomUser.objects.create_user(
            username="testuser",
            email="example@mail.de",
            password="testpassword",
            type=CustomUser.Roles.CUSTOMER,  # oder "customer"
        )

        # Existiert ein Profil?
        self.assertTrue(
            UserProfile.objects.filter(user=user).exists(),
            "UserProfile wurde nicht automatisch erstellt."
        )

        # Felder gespiegelt?
        profile = user.profile  # dank related_name="profile"
        self.assertEqual(profile.username, user.username)
        self.assertEqual(profile.email, user.email)
        self.assertEqual(profile.type, user.type)

                         


    