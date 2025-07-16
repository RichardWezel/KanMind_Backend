from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token


def validate_login_data(data):
    """
    Validate login input data.

    Checks whether the required fields 'email' and 'password' are present
    in the request data. If either is missing, returns an error response.

    Args:
        data (dict): The request data containing email and password.

    Returns:
        tuple:
            - email (str or None): The provided email address.
            - password (str or None): The provided password.
            - error_response (Response or None): A DRF Response object with error
              details, or None if validation passed.
    """

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return None, None, Response(
            {"detail": "You are not a member of this board. Please check your email and password."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return email, password, None


def get_user_token_response(user):
    """
    Generate a token response for an authenticated user.

    Retrieves or creates a token for the given user and returns
    a DRF Response containing the token and basic user info.

    Args:
        user (CustomUser): The authenticated user instance.

    Returns:
        Response: A JSON response with token, full name, email, and user ID,
        or an error message if something goes wrong.
    """

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
            {'detail': 'Internal server error.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
