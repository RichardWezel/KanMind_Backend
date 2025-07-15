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
    It handles the registration of new users by validating the input data,
    creating a new user, and returning a token for authentication.
    The 'fullname', 'email', and 'password' fields are required.
    The 'repeated_password' field is used to confirm the password.
    """
    permission_classes = [permissions.AllowAny] 

    # POST method to handle user registration
    def post(self, request, *args, **kwargs):
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
    It handles user authentication by checking the provided email and password.
    If the credentials are valid, it returns a token for authentication.
    The 'email' and 'password' fields are required.
    """
    permission_classes = [permissions.AllowAny]

    # POST method to handle user login
    def post(self, request, *args, **kwargs):
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