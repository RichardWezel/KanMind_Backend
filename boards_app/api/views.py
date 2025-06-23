
from boards_app.models import Board
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from boards_app.api.serializers import BoardSerializer
from django.db import models
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from .permissions import IsAuthenticatedWithCustomMessage


class BoardView(ListCreateAPIView):

    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage] 

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            models.Q(owner_id=user) | models.Q(members=user)
        ).distinct()

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(
                    {"detail": "Nicht autorisiert. Der Benutzer muss eingeloggt sein."},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            queryset = self.get_queryset()

            if not queryset.exists():
                return Response(
                    {"detail": "Du bist in keinem Board als Besitzer oder Mitglied eingetragen."},
                    status=status.HTTP_200_OK
                )

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "Interner Serverfehler.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(
                    {"detail": "Nicht autorisiert. Der Benutzer muss eingeloggt sein."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            

            serializer = BoardSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors,{'detail': 'Ungültige Anfragedaten.'},
                     status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            board = serializer.save(owner_id=user)
            board.members.add(user)
            board.member_count = board.members.count()
            board.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": "Interner Serverfehler.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedWithCustomMessage] 
    serializer_class = BoardSerializer

    def get_queryset(self):
        try:
            user = self.request.user
            return Board.objects.filter(
                models.Q(owner_id=user) | models.Q(members=user)
            ).distinct()
            
        except Exception as e:
            Response(
                {'detail': 'Interner Serverfehler.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
           
   

    def perform_update(self, serializer):
        board = self.get_object()
        user = self.request.user

        if board.owner_id != user:
            raise PermissionDenied("Nur der Besitzer darf das Board aktualisieren.")

        board = serializer.save()

        members = self.request.data.get('members', [])
        board.members.set(members + [user.id])
        board.member_count = board.members.count()
        board.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if instance.owner_id != user:
            raise PermissionDenied("Nur der Besitzer darf das Board löschen.")

        instance.delete()
