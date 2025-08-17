from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from profile_app.models import UserProfile
from profile_app.api.serializers import UserProfileSerializer
from rest_framework import generics
from django.http import Http404
from profile_app.api.serializers import FileUploadSerializer
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    View to retrieve a user's profile by primary key.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        try:
            obj = UserProfile.objects.get(pk=self.kwargs['pk'])
        except UserProfile.DoesNotExist:
            raise Http404("User profile does not exist")
        if obj.user != self.request.user:
            raise PermissionDenied("Not allowed to edit this profile.")
        return obj
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
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
    
class FileUploadView(APIView):
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)