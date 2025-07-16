from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from .utils import validate_login_data, get_user_token_response

from .serializers import RegistrationSerializer

User = get_user_model()

class RegistrationView(APIView):
    """
    View for user registration.

    Allows unauthenticated users to create an account by submitting their
    full name, email, password, and repeated password.

    On success:
        - Validates input data using the RegistrationSerializer
        - Creates a new user
        - Generates an auth token
        - Returns user information and token

    Returns:
        HTTP 201: If user is created successfully
        HTTP 400: If validation fails
        HTTP 500: On unexpected server error
    """
    permission_classes = [permissions.AllowAny] 

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to register a new user.

        Validates the provided data, saves the user, creates a token,
        and returns user details along with the token.

        Args:
            request: The HTTP request object containing user data.

        Returns:
            Response: A JSON response with user data and token or error details.
        """

        try:
            serializer = RegistrationSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors,
                     status=status.HTTP_400_BAD_REQUEST)
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'fullname': user.fullname,
                'email': user.email,
                'user_id': user.id,
            }
            return Response(
                data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'detail': 'Interner Serverfehler.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class CustomLoginView(APIView):
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
        
        email, password, error_response = validate_login_data(request.data)
        if error_response:
            return error_response

        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {"detail": "E-Mail oder Passwort ist falsch."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return get_user_token_response(user)