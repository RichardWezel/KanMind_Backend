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
        status=500
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
        return Task.objects.filter(
            models.Q(assignee=self.request.user) | models.Q(reviewer=self.request.user)
        ).distinct()

    def list(self, request, *args, **kwargs):

        try:
            if not request.user.is_authenticated:
                return Response(status=401)

            queryset = self.get_queryset().filter(assignee=request.user)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=200)
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
            if not request.user.is_authenticated:
                return Response(status=401)
            if not request.data:
                return Response(status=400)

            board_id = request.data.get('board')
            if not board_id or not Board.objects.filter(id=board_id).exists():
                return Response(status=404)

            for field in ['assignee_id', 'reviewer_id']:
                if request.data.get(field) == "":
                    request.data[field] = None

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            return Response(TaskSerializer(task).data, status=201)
        except ValidationError:
            return Response(status=400)
        except Exception as e:
            return internal_error_response_500(e)
    

class TaskReviewingView(ListAPIView):
    """This view lists all tasks that are currently under review by the user."""
    http_method_names = ['get'] 

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage] 

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user).distinct()

    def list(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return Response(status=401)
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=200)
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
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            return Response(TaskUpdateSerializer(task).data, status=200)
        except (ValidationError, PermissionDenied, Http404) as e:
            return Response({"detail": str(e)}, status=400 if isinstance(e, ValidationError) else 403 if isinstance(e, PermissionDenied) else 404)
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
            if not request.user.is_authenticated:
                return Response(status=401)

            try:
                pk = int(kwargs.get("pk", 0))
                if pk <= 0:
                    raise ValueError()
            except (TypeError, ValueError):
                return Response({"detail": "Ungültige Task-ID."}, status=400)

            instance = self.get_object()
            if instance.assignee != request.user and instance.board.owner_id != request.user.id:
                return Response({"detail": "Nur der Ersteller oder Board-Eigentümer darf löschen."}, status=403)

            self.perform_destroy(instance)
            return Response(status=204)
        except (Http404, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=404 if isinstance(e, Http404) else 403)
        except Exception as e:
            return internal_error_response_500(e)

    def perform_destroy(self, instance):
        instance.delete()  


class TaskCommentsView(generics.ListAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage]

    def get_queryset(self):
        try:
            return Task.objects.filter(
                models.Q(assignee=self.request.user) | models.Q(reviewer=self.request.user)
            ).distinct()
        except Exception as e:
            raise NotFound("Fehler beim Laden der Aufgaben: " + str(e))


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
        return Task.objects.filter(task__pk=self.kwargs.get('pk'))
    
    def get(self, request, *args, **kwargs):
        task = validate_pk_task(self.kwargs.get('pk'))
        serializer = self.get_serializer(task.comments.all(), many=True)
        return Response(serializer.data, status=200)

    def create(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                raise PermissionDenied("Du musst angemeldet sein.")
            task = validate_pk_task(self.kwargs.get('pk'))
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = serializer.save(author=request.user, task=task)
            task.comments_count = task.comments.count()
            task.save()
            return Response(self.get_serializer(comment).data, status=201)
        except (NotFound, ValidationError, PermissionDenied) as e:
            return Response({"detail": str(e)}, status=400 if isinstance(e, ValidationError) else 403 if isinstance(e, PermissionDenied) else 404)
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
        task = validate_pk_task(self.kwargs.get('task_id'))
        comment = validate_comment_in_task(self.kwargs.get('comment_id'), task)
        self.check_object_permissions(self.request, comment)
        return comment

    def perform_destroy(self, instance):
        task = instance.task
        instance.delete()
        task.comments_count = task.comments.count()
        task.save()
