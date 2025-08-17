from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from profile_app.models import UserProfile
from profile_app.api.serializers import UserProfileSerializer


class Profile(APIView):
    """
    View to retrieve a user's profile by primary key.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request, pk):
        try:
            profile = UserProfile.objects.get(pk=pk)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)