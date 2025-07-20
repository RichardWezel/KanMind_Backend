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
from rest_framework.exceptions import PermissionDenied, NotFound, ParseError
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, NotFound

from auth_app.models import CustomUser
from auth_app.api.serializers import UserSerializer  
from boards_app.models import Board
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer
from .permissions import IsAuthenticatedWithCustomMessage


def internal_error_response_500(exception):
    """
    Return a standardized internal server error response.

    Args:
        exception (Exception): The raised exception.

    Returns:
        Response: A DRF Response with a 500 status and error details.
    """

    return Response(
        {"error": "An internal server error has occurred.", "details": str(exception)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

class BoardView(ListCreateAPIView):
    """
    API view for listing and creating boards.

    GET:
        Returns a list of all boards where the authenticated user is the owner or a member.

    POST:
        Creates a new board. The authenticated user becomes the owner and is
        automatically added as a member. The request must include a 'title' and a
        list of 'members' (user IDs).

    Permissions:
        Requires authentication (custom permission with a helpful error message).
    """

    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage] 

    def get_queryset(self):
        """
        Return boards where the authenticated user is the owner or a member.
        """

        user = self.request.user
        return Board.objects.filter(
            models.Q(owner_id=user) | models.Q(members=user)
        ).distinct().order_by('id')

    def list(self, request, *args, **kwargs):
        """
        List all boards for the authenticated user.
        """

        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return internal_error_response_500(e)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new board owned by the authenticated user.

        The user is also added as a member, and the member count is updated.
        """
        try:
            # Absicherung: request.data parst JSON, kann aber bei kaputtem Input crashen
            if not isinstance(request.data, dict):
                raise ValidationError({"detail": "Invalid JSON format."})
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            board = serializer.save(owner_id=request.user)
            board.members.add(request.user)
            board.member_count = board.members.count()
            board.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ParseError:
            return Response(
                {"detail": "Invalid JSON in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        except ValidationError as ve:
            return Response(ve.detail, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return internal_error_response_500(e)
        

class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a specific board.

    GET:
        Retrieve board details including title, owner, members, and tasks.

    PATCH:
        Update title or members of the board (only for owner or members).

    DELETE:
        Delete the board (only allowed for the owner).

    Permissions:
        Only accessible to board owners and members.
    """

    permission_classes = [IsAuthenticatedWithCustomMessage] 

    def get_serializer_class(self):
        """
        Return the appropriate serializer depending on the request method.
        """

        if self.request.method == 'GET':
            return BoardDetailSerializer
        return BoardUpdateSerializer
    
    def get_object(self):
        """
        Retrieve the board instance and check user permissions.

        Raises:
            PermissionDenied: If the user has no access to this board.
        """

        board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        user = self.request.user
    
        if board.owner != user and not board.members.filter(id=user.id).exists():
            raise PermissionDenied("You do not have access to this board.")
    
        return board

    def update(self, request, *args, **kwargs):
        """
        Update board fields like title and members.

        Validates user IDs in the 'members' field and adds the current user to the list.
        """

        try:
            # Absicherung: request.data parst JSON, kann aber bei kaputtem Input crashen
            if not isinstance(request.data, dict):
                raise ValidationError({"detail": "Invalid JSON format."})
            
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

        except (PermissionDenied, NotFound, ValidationError, Http404) as e:
            raise e

        except Exception as e:
            return internal_error_response_500(e)

    def perform_update(self, serializer):
        """
        Save updated board data and update members list and count.
        """
           
        board = serializer.save()

        members = self.request.data.get('members', None)
        if members is not None:
            board.members.set(members + [self.request.user.id])

        board.member_count = board.members.count()
        board.save()

    # Deletes the board object if the user is the owner.
    def destroy(self, request, *args, **kwargs):
        """
        Delete the board if the authenticated user is the owner.
        """

        try:
            board = get_object_or_404(Board, pk=self.kwargs.get('pk'))

            if board.owner != request.user:
                raise PermissionDenied("Only the owner may delete the board.")

            self.perform_destroy(board)
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except (PermissionDenied, NotFound, Http404) as e:
            raise e
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_destroy(self, instance):
        """
        Delete the board instance from the database.
        """
        instance.delete()  


class EmailCheckView(APIView):
    """
    API view to check whether a user with the given email exists.

    GET:
        Query param: ?email=<email>
        - Returns user data if the email exists.
        - Returns 404 if no user is found.
        - Returns 400 if the email is invalid or missing.

    Permissions:
        Requires authentication.
    """

    permission_classes = [IsAuthenticatedWithCustomMessage]

    def get(self, request):
        """
        Validate the provided email and return the user data if found.

        Raises:
            ValidationError: If email is missing or invalid.
            NotFound: If no user exists with the given email.
        """
        
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
