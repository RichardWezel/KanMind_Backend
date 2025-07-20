from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import json
from rest_framework.exceptions import ParseError, ValidationError, NotFound

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Custom JSON parse error handler
    if isinstance(exc, ParseError):
        return Response(
            {"detail": "Invalid JSON. Make sure all keys and string values are in double quotes."},
            status=status.HTTP_400_BAD_REQUEST
        )

    return response