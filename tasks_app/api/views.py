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

def internal_error_response_500(e):
    """
    Return a standardized 500 Internal Server Error response.
    """
    return Response(
        {"error": str(e)},
        status=500
    )

def validate_pk_task(task_id):
    """
    Validate that a task with the given ID exists.

    Args:
        task_id (int): The ID of the task.

    Returns:
        Task: The task instance if found.

    Raises:
        NotFound: If no task exists with the given ID.
    """

    try:
        return Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise NotFound("Die angegebene Task existiert nicht.")

def validate_comment_in_task(comment_id, task):
    """
    Validate that a comment with the given ID exists for the specified task.

    Args:
        comment_id (int): The comment ID.
        task (Task): The parent task instance.

    Returns:
        TaskComment: The comment instance.

    Raises:
        NotFound: If the comment does not exist in the given task.
    """
     
    try:
        return task.comments.get(pk=comment_id)
    except TaskComment.DoesNotExist:
        raise NotFound("Comment not found.")


class TaskAssignedToMeView(ListCreateAPIView):
    """
    View to list all tasks assigned to the authenticated user.

    Only GET is allowed. Returns all tasks where the user is the assignee.
    """

    http_method_names = ['get'] 
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage] 

    def get_queryset(self):
        """
        Return all tasks where the current user is the assignee or reviewer.

        Returns:
            QuerySet: Filtered task queryset.
        """
        return Task.objects.filter(
            models.Q(assignee=self.request.user) | models.Q(reviewer=self.request.user)
        ).distinct()

    def list(self, request, *args, **kwargs):
        """
        Return a list of tasks where the user is the assignee.

        Returns:
            Response: JSON list of tasks.
        """
        try:
            queryset = self.get_queryset().filter(assignee=request.user)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return internal_error_response_500(e)
    

class CreateTaskView(CreateAPIView):
    """
    View to create a new task.

    Checks if the user is authenticated and a member of the specified board.
    Assignee/reviewer fields are optional and default to None.
    """

    http_method_names = ['post'] 
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage, IsAuthenticated, IsMemberOfBoard] 
 
    def post(self, request, *args, **kwargs):
        """
        Create and save a new task.

        Returns:
            Response: Serialized task on success, error on failure.
        """
        
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
    """
    View to list all tasks currently under review by the authenticated user.
    """
    http_method_names = ['get'] 

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage] 

    def get_queryset(self):
        """
        Return all tasks where the current user is the reviewer.

        Returns:
            QuerySet: Tasks to review.
        """
        
        return Task.objects.filter(reviewer=self.request.user).distinct()

    def list(self, request, *args, **kwargs):
        """
        Return serialized list of review tasks.

        Returns:
            Response: List of task data.
        """
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return internal_error_response_500(e)


class TaskUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific task.

    Permissions:
        - Only members of the associated board can access.
        - Only the assignee or board owner may delete the task.
    """

    permission_classes = [IsAuthenticatedWithCustomMessage, IsMemberOfBoard ]
    serializer_class = TaskUpdateSerializer
    
    def get_queryset(self):
        """
        Return all task objects.

        Returns:
            QuerySet: All tasks.
        """
        return Task.objects.all()
    
    def update(self, request, *args, **kwargs):
        """
        Update the task with provided data.

        Returns:
            Response: Updated task data.
        """
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
        """
        Delete the task if the user is the assignee or board owner.

        Returns:
            Response: 204 No Content.
        """
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
    """
    View to list all comments on tasks where the user is assignee or reviewer.
    """

    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage]

    def get_queryset(self):
        """
        Return all comments for tasks the user is assigned to or reviewing.

        Returns:
            QuerySet: Filtered comments.
        """

        try:
            user = self.request.user

            return TaskComment.objects.filter(
                models.Q(task__assignee=user) | models.Q(task__reviewer=user)
            ).select_related("task", "author").distinct().order_by("created_at")

        except Exception as e:
            raise NotFound(f"Error loading the comments: {str(e)}")


class TaskCreateCommentView(generics.ListCreateAPIView):
    """
    View to list and create comments for a specific task.

    Permissions:
        - Must be a board member of the task.
    """

    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticatedWithCustomMessage, IsMemberOfBoardComments]

    def get_queryset(self):
        """
        Return comments for the task specified in the URL.

        Returns:
            QuerySet: Task comments ordered by creation date.
        """
        
        task_id = self.kwargs.get('pk')
        task = self._get_task(task_id)
        return task.comments.select_related("author").order_by("created_at")

    def perform_create(self, serializer):
        """
        Save a new comment for the specified task and update the task's comment count.

        Args:
            serializer: Validated serializer instance.

        Returns:
            TaskComment: The created comment.
        """
        task = self._get_task(self.kwargs.get('pk'))
        comment = serializer.save(author=self.request.user, task=task)

        task.comments_count = task.comments.count()
        task.save()
        return comment

    def create(self, request, *args, **kwargs):
        """
        Handle POST request to add a comment to the task.

        Returns:
            Response: Created comment data.
        """
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
        """
        Helper to get the task by ID.

        Args:
            task_id (int): Task primary key.

        Returns:
            Task: Task instance.

        Raises:
            NotFound: If the task does not exist.
        """
        try:
            return Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise NotFound("The specified task does not exist.")


class TaskDeleteCommentView(generics.DestroyAPIView):
    """
    View to delete a specific comment from a task.

    Only the author of the comment may delete it, and only if they are a board member.
    """

    serializer_class = TaskCommentSerializer
    permission_classes = [
        IsAuthenticatedWithCustomMessage,
        IsMemberOfBoardComments,
        IsAuthorOfComment
    ]

    def get_object(self):
        """
        Return the comment instance based on task_id and comment_id.

        Returns:
            TaskComment: The comment instance.

        Raises:
            NotFound: If the task or comment is not found.
            PermissionDenied: If the user is not the author.
        """
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
        """
        Delete the comment if permissions are valid.

        Returns:
            Response: 204 No Content on success.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=204)

        except (PermissionDenied, NotFound) as e:
            raise e

        except Exception as e:
            return internal_error_response_500(e)

    def perform_destroy(self, instance):
        """
        Delete the comment and update the task's comment count.
    
        Args:
            instance (TaskComment): The comment to delete.
        """
        task = instance.task
        instance.delete()
        task.comments_count = task.comments.count()
        task.save()