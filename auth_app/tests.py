from rest_framework.test import APITestCase
from django.urls import reverse
from auth_app.models import CustomUser
from profile_app.models import UserProfile
from rest_framework import status

class RegistrationCreatesProfileTest(APITestCase):

    def test_register_creates_profile(self):
        url = reverse("auth_app:registration")  # Passe den URL-Namen an deine urls.py an
        payload = {
            "username": "apinewuser",
            "email": "apiuser@mail.de",
            "password": "SuperSecret123",
            "repeated_password": "SuperSecret123",
            "type": "customer",  # oder CustomUser.Roles.CUSTOMER
        }

        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, resp.data)

        user = CustomUser.objects.get(username="apinewuser")
        self.assertTrue(
            UserProfile.objects.filter(user=user).exists(),
            "UserProfile wurde nicht automatisch erstellt (API-Flow)."
        )

        profile = user.profile
        self.assertEqual(profile.username, "apinewuser")
        self.assertEqual(profile.email, "apiuser@mail.de")
        self.assertEqual(profile.type, "customer")
