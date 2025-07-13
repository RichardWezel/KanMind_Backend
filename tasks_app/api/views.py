from django.http import Http404
from django.db import models

from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError, PermissionDenied

from tasks_app.api.serializers import TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, TaskCommentSerializer
from tasks_app.models import Task, TaskComment
from boards_app.api.permissions import IsAuthenticatedWithCustomMessage
from boards_app.models import Board
from .permissions import IsMemberOfBoard, IsMemberOfBoardComments, IsAuthorOfComment




# This function handles internal server errors and returns a standardized response.
def internal_error_response_500(e):
    return Response(
        {"error": str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

# Validate the task ID and return the Task object or raise NotFound
def validate_pk_task(task_id):
    try:
        return Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise NotFound("Die angegebene Task existiert nicht.")

# Validate the comment ID in the context of a specific task
def validate_comment_in_task(comment_id, task):
    try:
        return task.comments.get(pk=comment_id)
    except TaskComment.DoesNotExist:
        raise NotFound("Kommentar nicht gefunden.")


class TaskAssignedToMeView(ListCreateAPIView):
    """This view lists all tasks assigned to the authenticated user."""
    http_method_names = ['get'] 

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage] 

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            models.Q(assignee=user) | models.Q(reviewer=user)
        ).distinct()

    def list(self, request, *args, **kwargs):

        try:
            user = request.user
            if not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            queryset = self.get_queryset()

            if not queryset.exists():
                return Response(status=status.HTTP_200_OK)

            queryset = queryset.filter(assignee=user)
            if not queryset.exists():
                return Response(status=status.HTTP_200_OK)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return internal_error_response_500(e)
    

class CreateTaskView(CreateAPIView):
    """
    This view handles the creation of a new task.
    It checks if the user is authenticated and a member of the board specified in the request.
    If the user is not authenticated or not a member, it raises a PermissionDenied error.
    The view expects the request data to contain a 'board' field, which is the ID
    of the board to which the task will be assigned.
    If the 'assignee_id' or 'reviewer_id' fields are empty, they
    will be set to None.
    """
    http_method_names = ['post'] 

    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage, IsAuthenticated, IsMemberOfBoard] 
 
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            if not request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            board_id = request.data.get('board')
            if not board_id or not Board.objects.filter(id=board_id).exists():
                return Response(status=status.HTTP_404_NOT_FOUND)
            
            if request.data.get('assignee_id') == "":
                request.data['assignee_id'] = None

            if request.data.get('reviewer_id') == "":
                request.data['reviewer_id'] = None

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            response_data = TaskSerializer(task).data 
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return internal_error_response_500(e)
    

class TaskReviewingView(ListAPIView):
    """This view lists all tasks that are currently under review by the user."""
    http_method_names = ['get'] 

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage] 

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(reviewer=user).distinct()

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


class TaskUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """"This view handles the update and deletion of a specific task."""
    permission_classes = [IsAuthenticatedWithCustomMessage, IsMemberOfBoard ]
    serializer_class = TaskUpdateSerializer
    
    def get_queryset(self):
        return Task.objects.all()
    
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            response_data = TaskUpdateSerializer(task).data 
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ValidationError as ve:
            return Response({"detail": ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        
        except PermissionDenied as e:
            return Response({'detail': str(e)}, status=status.HTTP_403_FORBIDDEN)

        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return internal_error_response_500(e)

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a task instance if the requesting user is authorized.
        This method performs the following steps:
        - Checks if the user is authenticated.
        - Validates the provided task ID (`pk`).
        - Retrieves the task instance, handling cases where it does not exist or access is denied.
        - Ensures that only the task assignee or the board owner can delete the task.
        - Deletes the task instance if all checks pass.
        Returns:
            - 204 NO CONTENT on successful deletion.
            - 400 BAD REQUEST if the task ID is invalid.
            - 401 UNAUTHORIZED if the user is not authenticated.
            - 403 FORBIDDEN if the user lacks permission.
            - 404 NOT FOUND if the task does not exist.
            - 500 INTERNAL SERVER ERROR for unexpected exceptions.
        """
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            pk = kwargs.get("pk")
            try:
                pk = int(pk)
                if pk <= 0:
                    raise ValueError()
            except (TypeError, ValueError):
                return Response({"detail": "Ungültige Task-ID."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                instance = self.get_object()
            except Http404:
                return Response({"detail": "Task wurde nicht gefunden."}, status=status.HTTP_404_NOT_FOUND)
            except PermissionDenied as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
            board = instance.board

            if instance.assignee != user and board.owner_id != user.id:
                return Response({"detail": "Nur der Ersteller oder Board-Eigentümer darf löschen."}, status=status.HTTP_403_FORBIDDEN)

            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return internal_error_response_500(e)

    def perform_destroy(self, instance):
        instance.delete()  


class TaskCommentsView(generics.ListAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage]

    def get_queryset(self):
        user = self.request.user
        try:
            return Task.objects.filter(
                models.Q(assignee=user) | models.Q(reviewer=user)
            ).distinct()
        except Task.DoesNotExist:
            raise NotFound("Task not found.")
        except Exception as e:
            return internal_error_response_500(e)


class TaskCreateCommentView(generics.ListCreateAPIView):
    """
    View to create comments for a specific task.
    This view allows authenticated users to add comments to a task.
    It checks if the user is a member of the board associated with the task.
    If the user is not authenticated or not a member, it raises a PermissionDenied error.
    """
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated, IsMemberOfBoardComments]

    def get_queryset(self):
        task_id = self.kwargs.get('pk')
        return Task.objects.filter(task__pk=task_id)
    
    def get(self, request, *args, **kwargs):
        task_id = self.kwargs.get('pk')
        task = validate_pk_task(task_id)
        comments = task.comments.all()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        try:
            user = self.request.user
            if not user.is_authenticated:
                raise PermissionDenied("Du musst angemeldet sein.")

            task_id = self.kwargs.get('pk')
            task = validate_pk_task(task_id)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save(author=user, task=task)
            task.comments_count = task.comments.count()
            task.save()

            return Response(self.get_serializer(comment).data, status=status.HTTP_201_CREATED)

        except NotFound as nf:
            return Response({"detail": str(nf)}, status=status.HTTP_404_NOT_FOUND)

        except ValidationError as ve:
            return Response({"detail": ve.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return internal_error_response_500(e)


class TaskDeleteCommentView(generics.DestroyAPIView):
    """
    View to delete a specific comment from a task.
    This view allows authenticated users to delete comments they authored.
    It checks if the user is a member of the board associated with the task and if they
    are the author of the comment.
    If the user is not authenticated, not a member, or not the author, it raises
    PermissionDenied or NotFound errors.
    """

    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated,  IsMemberOfBoardComments, IsAuthorOfComment]

    def get_object(self):
        task_id = self.kwargs.get('task_id')
        comment_id = self.kwargs.get('comment_id')
        if not task_id or not comment_id:
            raise NotFound("Task-ID oder Comment-ID fehlt oder ist ungültig.")
        task = validate_pk_task(task_id)
        comment = validate_comment_in_task(comment_id, task)
        if not comment:
            raise NotFound("Kommentar nicht gefunden.")
        self.check_object_permissions(self.request, comment)
        return comment

    def perform_destroy(self, instance):
        task = instance.task
        instance.delete()
        task.comments_count = task.comments.count()
        task.save()
