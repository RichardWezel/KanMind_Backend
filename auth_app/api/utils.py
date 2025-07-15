from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

# Utility functions for authentication views
def validate_login_data(data):
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return None, None, Response(
            {"detail": "E-Mail und Passwort sind erforderlich."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return email, password, None

# Function to get user token response
def get_user_token_response(user):
    try:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id,
        }, status=status.HTTP_200_OK)
    except Exception:
        return Response(
            {'detail': 'Interner Serverfehler.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
