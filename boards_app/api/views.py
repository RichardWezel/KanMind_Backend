
from boards_app.models import Board
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer
from django.db import models
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from .permissions import IsAuthenticatedWithCustomMessage, IsOwnerOrMemberOfBoard
from rest_framework.exceptions import NotFound, ValidationError
from auth_app.models import CustomUser






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
        

# This view handles the retrieval, update, and deletion of a specific board.
class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedWithCustomMessage, IsOwnerOrMemberOfBoard] #401, 403

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BoardDetailSerializer
        if self.request.method in ['PUT', 'PATCH']:
            return BoardUpdateSerializer
        if self.request.method == 'DELETE':
            return BoardUpdateSerializer
     

    def get_queryset(self):
        user = self.request.user
        try:
            return Board.objects.filter(
                models.Q(owner_id=user) | models.Q(members=user)
            ).distinct()
        except Board.DoesNotExist:
            raise NotFound("Board nicht gefunden. Die angegebene Board-ID existiert nicht.") #404
        
        except Exception as e:
            return Response(
                {"detail": "Interner Serverfehler.", "error": str(e)}, #500
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        request_members = self.request.data.get('members', [])
        valid_users = CustomUser.objects.filter(id__in=request_members)
        if valid_users.count() != len(request_members):
            raise ValidationError("Ungültige Anfragedaten. Möglicherweise sind einige Benutzer ungültig.") #400
        
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(
                {
                    "detail": "Das Board wurde erfolgreich aktualisiert. Mitglieder wurden hinzugefügt und/oder entfernt.",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except NotFound:
            return Response(
                {"detail": "Board nicht gefunden. Die angegebene Board-ID existiert nicht."}, #404
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": "Interner Serverfehler.", "error": str(e)}, #500
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def perform_update(self, serializer):
        
        user = self.request.user
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



