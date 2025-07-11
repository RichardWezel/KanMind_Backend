from tasks_app.api.serializers import TaskSerializer, TaskCreateSerializer, TaskUpdateSerializer, TaskCommentSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from boards_app.api.permissions import IsAuthenticatedWithCustomMessage
from tasks_app.models import Task, TaskComment
from django.db import models
from .permissions import IsMemberOfBoard
from boards_app.models import Board
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView




def internal_error_response_500(e):
    return Response(
        {"error": str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

# Validate the primary key of a task
def validate_pk_task(task_id):
    try:
        task = Task.objects.get(pk=task_id)
        return task
    except Task.DoesNotExist:
         Response(status=status.HTTP_404_NOT_FOUND)

def validate_comment_in_task(comment_id, task):
    try:
        comment = task.comments.get(pk=comment_id)
    except TaskComment.DoesNotExist:
            Response(status=status.HTTP_404_NOT_FOUND)

class TaskAssignedToMeView(ListCreateAPIView):
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
    http_method_names = ['post'] 

    serializer_class = TaskCreateSerializer
    permission_classes = [IsMemberOfBoard, IsAuthenticatedWithCustomMessage, IsAuthenticated] 

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            if not hasattr(request, 'data') or not request.data:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            response_data = TaskSerializer(task).data 
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return internal_error_response_500(e)
    
class TaskReviewingView(ListAPIView):
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
    permission_classes = [IsMemberOfBoard, IsAuthenticatedWithCustomMessage]
    serializer_class = TaskUpdateSerializer
    
    def get_queryset(self):
        user = self.request.user
        try:
            return Task.objects.filter(
                models.Q(assignee=user)
            ).distinct()
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return internal_error_response_500(e)
    
    def update(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            instance = self.get_object()  # die Task

            board = instance.board
            if user not in board.members.all() and user != board.owner_id:
                return Response(status=status.HTTP_403_FORBIDDEN)
            
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            response_data = TaskUpdateSerializer(task).data 
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return internal_error_response_500(e)

    def destroy(self, request, *args, **kwargs):
        try:
            user = request.user
            instance = self.get_object()

            pk = kwargs.get("pk")
            try:
                pk = int(pk)
                if pk <= 0:
                    raise ValueError()
            except (TypeError, ValueError):
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if not user.is_authenticated:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            
            board = instance.board
            if user not in board.members.all() and user != board.owner_id:
                return Response(status=status.HTTP_403_FORBIDDEN)
            
            if instance.assignee != user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            
            if not instance:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
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

# View to list comments for a specific task
class TaskCreateCommentView(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]

    # Get the queryset for comments related to a specific task
    # This is used to filter comments by task ID
    def get_queryset(self):
        task_id = self.kwargs.get('pk')
        return Task.objects.filter(task__pk=task_id)
    
    # Retrieve comments for a specific task
    def get(self, request, *args, **kwargs):
        task_id = self.kwargs.get('pk')
        task = validate_pk_task(task_id)
        comments = task.comments.all()
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Perform the creation of a comment
    def perform_create(self, serializer):
        task_id = self.kwargs.get('pk')
        task = validate_pk_task(task_id)

        # saves comment with the current user and task
        comment = serializer.save(author=self.request.user, task=task)

        # update comment count for the task
        task.comments_count = task.comments.count()
        task.save()

# View to delete a specific comment from a task
class TaskDeleteCommentView(generics.DestroyAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]

    # Retrieve the comment object based on task_id and comment_id
    def get_object(self):
        task_id = self.kwargs.get('task_id')
        comment_id = self.kwargs.get('comment_id')

        # Validate task_id and comment_id
        if not task_id:
            Response(status=status.HTTP_400_BAD_REQUEST)
        if not comment_id:
            Response(status=status.HTTP_400_BAD_REQUEST)

        # Check if the task exists
        task = validate_pk_task(task_id)

        # Check if the comment exists for the task
        comment = validate_comment_in_task(comment_id, task)
        return comment

    # Delete the comment and update the task's comment count
    def perform_destroy(self, instance):
        task = instance.task
        instance.delete()

        # update comment count for the task
        task.comments_count = task.comments.count()
        task.save()
