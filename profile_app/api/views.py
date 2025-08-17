from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from profile_app.models import UserProfile
from profile_app.api.serializers import UserProfileSerializer
from rest_framework import generics
from django.http import Http404
from profile_app.api.serializers import FileUploadSerializer


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    View to retrieve a user's profile by primary key.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_serializer_class(self):
        return UserProfileSerializer if self.request.method == 'GET' else super().get_serializer_class()
  
    def get_object(self):
        try:
            return UserProfile.objects.get(pk=self.kwargs['pk'])
        except UserProfile.DoesNotExist:
            raise Http404("User profile does not exist ")
        
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
class FileUploadView(APIView):
    def post(self, request, format=None):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)