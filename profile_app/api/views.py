from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, generics, serializers

from profile_app.models import UserProfile
from .serializers import UserProfileSerializer, FileUploadSerializer, TypeSpecificProfileSerializer
from auth_app.models import CustomUser
from .permissions import UpdatingUserIsProfileUser


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update a single user profile.

    Enforces IsAuthenticated and object-level ownership via
    UpdatingUserIsProfileUser.
    """
    permission_classes = [IsAuthenticated, UpdatingUserIsProfileUser]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        """Fetch the UserProfile by pk and check object permissions."""
        try:
            obj = UserProfile.objects.get(pk=self.kwargs['pk'])
        except UserProfile.DoesNotExist:
            raise Http404("User profile does not exist")
        # Enforce object-level permissions
        self.check_object_permissions(self.request, obj)
        return obj
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Update profile and optionally synchronize email on the user model.

        Supports PATCH (partial) and PUT (full) updates.
        Performs uniqueness validation for email if provided.
        """

        partial = kwargs.pop('partial', request.method.upper() == 'PATCH')
        instance = self.get_object()

        raw_email = request.data.get('email', None)
        if raw_email is not None:
            email = serializers.EmailField().to_internal_value(raw_email)

            User = get_user_model()
            if User.objects.filter(email=email).exclude(pk=instance.user.pk).exists():
                return Response(
                    {"email": "This email is already in use."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            instance.user.email = email
            instance.user.save(update_fields=["email"])

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
    
class BussinessProfileView(generics.ListAPIView):
    """List all business user profiles (requires authentication)."""
    permission_classes = [IsAuthenticated]
    serializer_class = TypeSpecificProfileSerializer
    
    def get_queryset(self):
        """Return queryset of profiles where user type is BUSINESS."""
        return UserProfile.objects.filter(user__type=CustomUser.Roles.BUSINESS)

    def list(self, request, *args, **kwargs):
        """Serialize and return the list of business profiles."""
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

class CustomerProfileView(generics.ListAPIView):
    """List all customer user profiles (requires authentication)."""
    permission_classes = [IsAuthenticated]
    serializer_class = TypeSpecificProfileSerializer
    
    def get_queryset(self):
        """Return queryset of profiles where user type is CUSTOMER."""
        return UserProfile.objects.filter(user__type=CustomUser.Roles.CUSTOMER)

    def list(self, request, *args, **kwargs):
        """Serialize and return the list of customer profiles."""
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
    
class FileUploadView(APIView):
    """Upload a file and persist via FileUpload model."""

    def post(self, request, format=None):
        """Validate and save uploaded file, return its metadata."""
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
