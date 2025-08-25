from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics, serializers

from profile_app.models import UserProfile
from profile_app.api.serializers import UserProfileSerializer, FileUploadSerializer, TypeSpecificProfileSerializer
from auth_app.models import CustomUser

class OrdersView(APIView):
    pass

class OrderUpdateDeleteView(APIView):
    pass