
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
from auth_app.api.serializers import UserSerializer  
from django.shortcuts import get_object_or_404
from django.http import Http404

def internal_error_response_500(e):
    return Response(
        {"error": str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

# This view handles the listing and creation of boards.
class BoardView(ListCreateAPIView):

    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage] 

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            models.Q(owner_id=user) | models.Q(members=user)
        ).distinct().order_by('id')

    def list(self, request, *args, **kwargs):
     

        try:
            user = request.user
            if not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response(status=status.HTTP_200_OK)
         
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return internal_error_response_500(e)
        
    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            serializer = BoardSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            board = serializer.save(owner_id=user)
            board.members.add(user)
            board.member_count = board.members.count()
            board.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return internal_error_response_500(e)
        

# This view handles the retrieval, update, and deletion of a specific board.
class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedWithCustomMessage] #401

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BoardDetailSerializer
        if self.request.method in ['PUT', 'PATCH']:
            return BoardUpdateSerializer
        if self.request.method == 'DELETE':
            return BoardUpdateSerializer
     
    def get_object(self):
        board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        user = self.request.user
    
        if board.owner_id != user and not board.members.filter(id=user.id).exists():
            raise PermissionDenied("Du hast keinen Zugriff auf dieses Board.")
    
        return board

        
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
    
            # ZUERST: Zugriffsschutz mit get_object (liefert 403 oder 404)
            instance = self.get_object()
    
            # DANN: Validierung der Mitglieder
            request_members = self.request.data.get('members', [])
            valid_users = CustomUser.objects.filter(id__in=request_members)
            if valid_users.count() != len(request_members):
                return Response(status=status.HTTP_400_BAD_REQUEST)
    
            # Danach PATCH mit Instanz
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
        except PermissionDenied as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)
    
        except Http404:
            return Response({'detail': 'Board wurde nicht gefunden.'}, status=status.HTTP_404_NOT_FOUND)
    
        except Exception as e:
            return internal_error_response_500(e)

        
    def perform_update(self, serializer):
        
        user = self.request.user
        board = serializer.save()
        members = self.request.data.get('members', [])
        board.members.set(members + [user.id])
        board.member_count = board.members.count()
        board.save()


    def destroy(self, request, *args, **kwargs):
        try:
            user = request.user
            instance = self.get_object()

            if not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            if instance.owner_id != user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except NotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return internal_error_response_500(e)

    def perform_destroy(self, instance):
        instance.delete()  


class EmailCheckView(APIView):
    permission_classes = [IsAuthenticatedWithCustomMessage]

    def get(self, request):
        email = request.query_params.get("email")

        if not email:
            return Response({"detail": "E-Mail-Parameter fehlt."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Kein Benutzer mit dieser E-Mail gefunden."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return internal_error_response_500(e)
