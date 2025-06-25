from tasks_app.api.serializers import TaskSerializer, TaskCreateSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from boards_app.api.permissions import IsAuthenticatedWithCustomMessage
from tasks_app.models import Task
from django.db import models
from .permissions import IsMemberOfBoard
from boards_app.models import Board
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

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
                return Response(
                    {"detail": "Nicht autorisiert. Der Benutzer muss eingeloggt sein, um auf diese Tasks zugreifen zu können."},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            queryset = self.get_queryset()

            if not queryset.exists():
                return Response(
                    {"detail": "Erfolgreich. Gibt eine Liste der Tasks zurück, bei denen der Benutzer als Prüfer (`reviewer`) eingetragen ist."},
                    status=status.HTTP_200_OK
                )

            queryset = queryset.filter(assignee=user)
            if not queryset.exists():
                return Response(
                    {"detail": "Du bist in keiner Tasks als Prüfer (`reviewer`) eingetragen."},
                    status=status.HTTP_200_OK
                )
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "Interner Serverfehler.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class CreateTaskView(CreateAPIView):
    http_method_names = ['post'] 

    serializer_class = TaskCreateSerializer
    permission_classes = [IsMemberOfBoard, IsAuthenticatedWithCustomMessage, IsAuthenticated] 

    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user.is_authenticated:
                return Response(
                    {"detail": "Nicht autorisiert. Der Benutzer muss eingeloggt sein, um auf diese Tasks zugreifen zu können."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if not hasattr(request, 'data') or not request.data:
                return Response(
                    {"detail": "Ungültige Anfragedaten. Möglicherweise fehlen erforderliche Felder oder enthalten ungültige Werte."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            response_data = TaskSerializer(task).data 
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"detail": "Interner Serverfehler.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
                return Response(
                    {"detail": "Nicht autorisiert. Der Benutzer muss eingeloggt sein, um auf diese Tasks zugreifen zu können."},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            queryset = self.get_queryset()

            if not queryset.exists():
                return Response(
                    {"detail": "Du hast keine Aufgaben in deinen Boards."},
                    status=status.HTTP_200_OK
                )

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": "Interner Serverfehler.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    