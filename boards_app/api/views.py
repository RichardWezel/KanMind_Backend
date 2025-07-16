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
from rest_framework.exceptions import ValidationError, NotFound

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

    # Retrieves the queryset of boards for the authenticated user.
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            models.Q(owner_id=user) | models.Q(members=user)
        ).distinct().order_by('id')

    # Lists all boards for the authenticated user.
    def list(self, request, *args, **kwargs):
     
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return internal_error_response_500(e)
    
    # Creates a new board for the authenticated user.
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_queryset()
            serializer.is_valide(raise_exception=True)

            board = serializer.save(owner_id=request.user)
            board.members.add(request.user)
            board.member_count = board.members.count()
            board.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as ve:
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
        
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

    # Retrieves the board object based on the primary key (pk) provided in the URL.
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BoardDetailSerializer
        return BoardUpdateSerializer
    
    # Retrieves the board object for the authenticated user.
    def get_object(self):
        board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        user = self.request.user
    
        if board.owner_id != user and not board.members.filter(id=user.id).exists():
            raise PermissionDenied("You do not have access to this board.")
    
        return board

    # Updates the board object with the provided data.
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()

            request_members = self.request.data.get('members', [])
            valid_users = CustomUser.objects.filter(id__in=request_members)

            if valid_users.count() != len(request_members):
                raise ValidationError({"members": "One or more user IDs are invalid."})

            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (PermissionDenied, NotFound, ValidationError) as e:
            raise e

        except Exception as e:
            return internal_error_response_500(e)

    # Performs the update operation on the board instance.
    def perform_update(self, serializer):
        board = serializer.save()

        members = self.request.data.get('members', None)
        if members is not None:
            board.members.set(members + [self.request.user.id])

        board.member_count = board.members.count()
        board.save()

    # Deletes the board object if the user is the owner.
    def destroy(self, request, *args, **kwargs):
        try:
            board = self.get_object()

            if board.owner_id != request.user.id:
                raise PermissionDenied("Only the owner may delete the board.")

            self.perform_destroy(board)
            return Response({}, status=status.HTTP_200_OK)

        except (PermissionDenied, NotFound) as e:
            raise e
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Performs the deletion of the board instance.
    def perform_destroy(self, instance):
        instance.delete()  


class EmailCheckView(APIView):
    """
    This view checks if a user with the given email exists.
    It returns the user data if found, or a 404 error if not.
    """
    permission_classes = [IsAuthenticatedWithCustomMessage]

    # Retrieves user data based on the provided email query parameter.
    def get(self, request):
        try:
            email = request.query_params.get("email", "").strip()

            if not email:
                raise ValidationError({"email": "E-mail parameter is missing."})

            try:
                validate_email(email)
            except EmailNotValidError:
                raise ValidationError({"email": "Unvalid email address."})


            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                    raise NotFound("No user found with this email address.")

            serializer = UserSerializer(user)
            return Response(serializer.data)
        
        except (ValidationError, NotFound) as e:
            raise e  
        
        except Exception as e:
            return internal_error_response_500(e)
