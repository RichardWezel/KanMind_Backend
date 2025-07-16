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
            queryset = self.get_queryset().filter(assignee=request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
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
            data = request.data

            if not data:
                raise ValidationError({"detail": "Request-data is missing"})

            board_id = data.get('board')
            if not board_id or not Board.objects.filter(id=board_id).exists():
                raise NotFound("The specified board does not exist.")

            for field in ['assignee_id', 'reviewer_id']:
                if data.get(field) == "":
                    data[field] = None

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            task = serializer.save()

            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)

        except (ValidationError, NotFound) as e:
            raise e 

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
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
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
            serializer = self.get_serializer(
                instance, 
                data=request.data, 
                partial=kwargs.pop('partial', False)
            )
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)
        
        except (ValidationError, PermissionDenied, Http404, NotFound) as e:
            raise e  

        except Exception as e:
            return internal_error_response_500(e)


    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            if instance.assignee != request.user and instance.board.owner_id != request.user.id:
                raise PermissionDenied("Only the editor or the board owner may delete the task and the specified board does not exist.")

            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        except (PermissionDenied, Http404, NotFound) as e:
            raise e

        except Exception as e:
            return internal_error_response_500(e)


class TaskCommentsView(generics.ListAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage]

    def get_queryset(self):
        try:
            user = self.request.user

            return TaskComment.objects.filter(
                models.Q(task__assignee=user) | models.Q(task__reviewer=user)
            ).select_related("task", "author").distinct().order_by("created_at")

        except Exception as e:
            raise NotFound(f"Error loading the comments: {str(e)}")


class TaskCreateCommentView(generics.ListCreateAPIView):
    """
    This view handles the creation of comments for a specific task.
    """
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage, IsMemberOfBoardComments]

    def get_queryset(self):
        task_id = self.kwargs.get('pk')
        task = self._get_task(task_id)
        return task.comments.select_related("author").order_by("created_at")

    def perform_create(self, serializer):
        task = self._get_task(self.kwargs.get('pk'))
        comment = serializer.save(author=self.request.user, task=task)

        task.comments_count = task.comments.count()
        task.save()
        return comment

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            comment = self.perform_create(serializer)
            return Response(self.get_serializer(comment).data, status=status.HTTP_201_CREATED)

        except (NotFound, ValidationError, PermissionDenied) as e:
            raise e

        except Exception as e:
            return internal_error_response_500(e)

    def _get_task(self, task_id):
        try:
            return Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise NotFound("The specified task does not exist.")


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
    permission_classes = [
        IsAuthenticatedWithCustomMessage,
        IsMemberOfBoardComments,
        IsAuthorOfComment
    ]

    def get_object(self):
        try:
           task_id = self.kwargs.get('task_id')
           comment_id = self.kwargs.get('comment_id')
           task = Task.objects.get(pk=task_id)
           comment = task.comments.get(pk=comment_id)
           self.check_object_permissions(self.request, comment)
           return comment

        except Task.DoesNotExist:
            raise NotFound("Task does not exist.")

        except Task.comments.model.DoesNotExist:
            raise NotFound("Comment does not exist.")

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=204)

        except (PermissionDenied, NotFound) as e:
            raise e

        except Exception as e:
            return internal_error_response_500(e)

    def perform_destroy(self, instance):
        task = instance.task
        instance.delete()
        task.comments_count = task.comments.count()
        task.save()