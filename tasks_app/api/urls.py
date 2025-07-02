from django.contrib import admin
from django.urls import path, include
from auth_app.api.views import RegistrationView, CustomLoginView
from boards_app.api.views import BoardView, BoardDetailView
from .views import TaskAssignedToMeView, TaskReviewingView
from tasks_app.api.views import CreateTaskView, TaskUpdateView, TaskCreateCommentView, TaskDeleteCommentView

urlpatterns = [
    path('', CreateTaskView.as_view(), name='task-create'),
    path('assigned-to-me/', TaskAssignedToMeView.as_view(), name='assigned-to-me'),
    path('reviewing/', TaskReviewingView.as_view(), name='task-reviewing'),
    path('<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
    path('<int:pk>/comments/', TaskCreateCommentView.as_view(), name='task-comments'),
    path('<int:task_id>/comments/<int:comment_id>', TaskDeleteCommentView.as_view(), name='task-delete-comment'),
]


