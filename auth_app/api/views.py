from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model

from .serializers import RegistrationSerializer

User = get_user_model()

class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny] 

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
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
   
            email = request.data.get('email')
            password = request.data.get('password')

            if not email or not password:
                return Response(
                    {"detail": "E-Mail und Passwort sind erforderlich."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = authenticate(request, username=email, password=password)

                if user is None:
                    return Response(
                    {"detail": "E-Mail oder Passwort ist falsch."},
                    status=status.HTTP_400_BAD_REQUEST  # Hier 400 statt 401
                )

                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'fullname': user.fullname,
                    'email': user.email,
                    'user_id': user.id,
                }, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response(
                    {'detail': 'Interner Serverfehler.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )