from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from .utils import validate_login_data, get_user_token_response
from rest_framework.authentication import TokenAuthentication

from .serializers import RegistrationSerializer

User = get_user_model()

class RegistrationView(APIView):
    """Register a new user and return an auth token."""
    
    permission_classes = [permissions.AllowAny] 
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        """Validate registration payload, create user and return token."""

        try:
            serializer = RegistrationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors,
                     status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
            }
            return Response(
                data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'detail': 'internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class LoginView(APIView):
    """
    View for user login.

    Allows users to log in by providing email and password.
    If the credentials are valid, a token is generated and returned.

    Uses:
        - `validate_login_data` for input validation
        - Django's `authenticate` to check credentials
        - `get_user_token_response` to build the response

    Returns:
        HTTP 200: If login is successful
        HTTP 400: If credentials are invalid or data is missing
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user login.

        Validates login data, authenticates the user, and returns an auth token.

        Args:
            request: The HTTP request object containing email and password.

        Returns:
            Response: A JSON response with user data and token or error message.
        """
        
        username, password, error_response = validate_login_data(request.data)
        if error_response:
            return error_response

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "email or password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return get_user_token_response(user)
