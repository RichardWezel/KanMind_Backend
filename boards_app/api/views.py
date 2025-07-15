from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import models
from email_validator import validate_email, EmailNotValidError

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from auth_app.models import CustomUser
from auth_app.api.serializers import UserSerializer  
from boards_app.models import Board
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer
from .permissions import IsAuthenticatedWithCustomMessage


# This function handles internal server errors and returns a standardized response.
def internal_error_response_500(exception):
    return Response(
        {"error": "Ein interner Serverfehler ist aufgetreten.", "details": str(exception)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

class BoardView(ListCreateAPIView):
    """
    This view handles the listing and creation of boards.
    It checks if the user is authenticated and has permission to access the boards.
    If the user is not authenticated, it raises a PermissionDenied error.
    The view expects the request to contain a 'members' field, which is a list of
    user IDs to be added as members of the board.
    If the 'members' field is not provided, it will not add any members to the board.
    """

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
                return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
            queryset = self.get_queryset()
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
        

class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    This view handles the retrieval, update, and deletion of a specific board.
    It checks if the user is authenticated and has permission to access the board.
    If the user is not authenticated or does not have permission, it raises a PermissionDenied error
    or NotFound error.
    The view expects the request to contain a 'members' field, which is a list of
    user IDs to be added as members of the board.
    If the 'members' field is not provided, it will not update the members of the
    board, but will still allow the owner to update other fields.
    """
    permission_classes = [IsAuthenticatedWithCustomMessage] 

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BoardDetailSerializer
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
            instance = self.get_object()
            request_members = self.request.data.get('members', [])

            valid_users = CustomUser.objects.filter(id__in=request_members)
            if valid_users.count() != len(request_members):
                return Response(status=status.HTTP_400_BAD_REQUEST)

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

        members = self.request.data.get('members', None)
        if members is not None:
            board.members.set(members + [user.id])

        board.member_count = board.members.count()
        board.save()


    def destroy(self, request, *args, **kwargs):
        try:
            board = self.get_object()

            if board.owner_id != request.user.id:
                raise PermissionDenied("Nur der Eigentümer darf das Board löschen.")

            self.perform_destroy(board)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Http404:
            return Response({"detail": "Board wurde nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
        
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_destroy(self, instance):
        instance.delete()  


class EmailCheckView(APIView):
    """
    This view checks if a user with the given email exists.
    It returns the user data if found, or a 404 error if not.
    """
    permission_classes = [IsAuthenticatedWithCustomMessage]

    def get(self, request):
        email = request.query_params.get("email", "").strip()

        if not email:
            return Response(
                {"detail": "E-Mail-Parameter fehlt."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_email(email)
        except EmailNotValidError:
            return Response(
                {"detail": "Ungültige E-Mail-Adresse."}, 
                status=400
            )
        
        try:
            user = CustomUser.objects.get(email=email)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "Kein Benutzer mit dieser E-Mail gefunden."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            return internal_error_response_500(e)
